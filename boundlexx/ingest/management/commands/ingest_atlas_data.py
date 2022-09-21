import gzip
import itertools
import os
import shutil
import tempfile
import zipfile
from io import BytesIO
from struct import unpack_from
from subprocess import run

import djclick as click
import requests
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from boundlexx.api.tasks import purge_static_cache
from boundlexx.boundless.models import (
    Beacon,
    BeaconPlotColumn,
    BeaconScan,
    Color,
    World,
)
from boundlexx.boundless.utils import SPHERE_GAP, crop_world, html_name
from boundlexx.utils import make_thumbnail

BASE_DIR = "/tmp/maps"
GLOW_SOLID = 5
GLOW_WIDTH = 20
BLEND_START = 1
BLEND_END = 0
TRANS_START = 255
TRANS_END = 128
BLUR = 10


def _draw_world_image(  # pylint: disable=too-many-locals
    atlas_image_file, world_id, atmo_color
):
    sphere_image_file = os.path.join(BASE_DIR, f"{world_id}_sphere.png")
    run(
        ["/usr/local/bin/convert-atlas", atlas_image_file, sphere_image_file],
        check=True,
        capture_output=True,
    )

    img = crop_world(Image.open(sphere_image_file))
    size, _ = img.size

    trans_diff = TRANS_START - TRANS_END
    blur_diff = BLEND_START - BLEND_END
    for offset in range(GLOW_WIDTH):
        offset = max(0, offset - GLOW_SOLID)

        trans = TRANS_START - int(offset / GLOW_WIDTH * trans_diff)
        blend = BLEND_START - offset / GLOW_WIDTH * blur_diff

        ellipse_coors = (
            SPHERE_GAP + offset,
            SPHERE_GAP + offset,
            size - SPHERE_GAP - offset,
            size - SPHERE_GAP - offset,
        )

        # add atmo color
        atmo = img.copy()
        drawa = ImageDraw.Draw(atmo)
        drawa.ellipse(
            ellipse_coors,
            outline=(*atmo_color, trans),
            width=2,
        )

        img = Image.blend(img, atmo, blend)

    outer_width = 2
    outer_ellipse = (
        SPHERE_GAP - outer_width,
        SPHERE_GAP - outer_width,
        size - SPHERE_GAP + outer_width,
        size - SPHERE_GAP + outer_width,
    )
    drawa = ImageDraw.Draw(img)
    drawa.ellipse(
        outer_ellipse,
        outline=(0, 0, 0, 255),
        width=outer_width,
    )

    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        outer_ellipse,
        outline=255,
        width=outer_width * 2,
    )

    blurred = img.filter(ImageFilter.GaussianBlur(BLUR))
    img.paste(blurred, mask=mask)

    with BytesIO() as output:
        img.save(output, format="PNG")
        content = output.getvalue()

    image = ContentFile(content)
    image.name = f"{world_id}.png"
    return image


def _process_image(world, root, name):
    atlas_image_file = os.path.join(root, name)

    img = Image.open(atlas_image_file)
    ImageOps.flip(img)
    img.save(atlas_image_file)

    with open(atlas_image_file, "rb") as image_file:
        atlas_image = ContentFile(image_file.read())
        atlas_image.name = f"{world.id}.png"

    image = _draw_world_image(atlas_image_file, world.id, world.atmosphere_color_tuple)

    if world.atlas_image is not None and world.atlas_image.name:
        world.atlas_image.delete()

    if world.image is not None and world.image.name:
        world.image.delete()

    if world.image_small is not None and world.image_small.name:
        world.image_small.delete()

    world.atlas_image = atlas_image
    world.image = image
    world.image_small = make_thumbnail(image)
    world.save()


def _process_beacons(world, root, name):  # pylint: disable=too-many-locals
    Beacon.objects.filter(world=world).delete()

    with gzip.open(os.path.join(root, name)) as beacons_file:
        buffer = beacons_file.read()

    if len(buffer) == 0:
        return

    # adapted from https://docs.playboundless.com/modding/http-beacons.html
    offset = 0

    num_beacons, world_size = unpack_from("<HH", buffer, offset)
    offset += 4

    colors = Color.objects.all()
    beacons = []
    for _ in range(num_beacons):
        skipped = unpack_from("<H", buffer, offset)[0]
        offset += 2

        if skipped != 0:
            num_beacons -= skipped
            break

        campfire, pos_x, pos_y, pos_z, mayor_name_len = unpack_from(
            "<BhhhB", buffer, offset
        )
        offset += 8
        mayor_name = unpack_from(f"<{mayor_name_len}s", buffer, offset)[0]
        mayor_name = mayor_name.decode("utf-8")
        offset += mayor_name_len

        beacon = Beacon.objects.create(
            world=world,
            location_x=pos_x,
            location_y=pos_y,
            location_z=-pos_z,
            is_campfire=bool(campfire),
        )

        if campfire != 0:
            BeaconScan.objects.create(beacon=beacon, mayor_name=mayor_name)
        else:
            prestige, compactness, num_plots, num_plot_columns, name_len = unpack_from(
                "<QbIIB", buffer, offset
            )
            offset += 18
            name = unpack_from(f"<{name_len}s", buffer, offset)[0]
            name = name.decode("utf-8")
            offset += name_len

            BeaconScan.objects.create(
                beacon=beacon,
                mayor_name=mayor_name,
                name=name,
                text_name=html_name(name, strip=True, colors=colors),
                html_name=html_name(name, colors=colors),
                prestige=prestige,
                compactness=compactness,
                num_plots=num_plots,
                num_columns=num_plot_columns,
            )
        beacons.append(beacon)

    for z, x in itertools.product(range(world_size), repeat=2):
        beacon_index, plot_count = unpack_from("<HB", buffer, offset)
        offset += 3
        if beacon_index != 0:
            BeaconPlotColumn.objects.create(
                beacon=beacons[beacon_index - 1], plot_x=x, plot_z=z, count=plot_count
            )


@click.command()
@click.argument("dropbox_url", nargs=1)
def command(dropbox_url):
    click.echo("Downloading zip...")
    response = requests.get(dropbox_url)
    response.raise_for_status()

    click.echo("Writing zip...")
    atlas_zip_file = tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
        delete=False
    )
    atlas_zip_file.write(response.content)
    atlas_zip_file.close()

    os.makedirs(BASE_DIR)

    with zipfile.ZipFile(atlas_zip_file.name, "r") as zip_file:
        zip_file.extractall(BASE_DIR)

    click.echo("Processing data...")
    for root, _, files in os.walk(BASE_DIR):
        with click.progressbar(files, show_percent=True, show_pos=True) as pbar:
            for name in pbar:
                pbar.label = name
                pbar.render_progress()
                world_id = int(name.split("_")[1])
                world = World.objects.filter(id=world_id).first()

                if world is None:
                    continue

                if name.endswith(".png"):
                    _process_image(world, root, name)
                elif name.endswith(".beacons.gz"):
                    _process_beacons(world, root, name)

    click.echo("Cleaning up...")
    os.remove(atlas_zip_file.name)
    shutil.rmtree(BASE_DIR)

    click.echo("Purging CDN cache...")
    purge_static_cache(["worlds", "atlas"])
