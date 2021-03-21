import gzip
import itertools
import os
import shutil
import tempfile
import zipfile
from struct import unpack_from

import djclick as click
import requests
from django.core.files.base import ContentFile

from boundlexx.boundless.models import (
    Beacon,
    BeaconPlotColumn,
    BeaconScan,
    Color,
    World,
)
from boundlexx.boundless.utils import html_name

BASE_DIR = "/tmp/maps"


def _process_image(world, root, name):
    with open(os.path.join(root, name), "rb") as atlas_image:
        image = ContentFile(atlas_image.read())
        image.name = f"{world.id}.png"

        if world.atlas_image is not None and world.atlas_image.name:
            world.atlas_image.delete()

        world.atlas_image = image
        world.save()


def _process_beacons(world, root, name):  # pylint: disable=too-many-locals
    Beacon.objects.filter(world=world).delete()

    with gzip.open(os.path.join(root, name)) as beacons_file:
        buffer = beacons_file.read()

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
    atlas_zip_file = tempfile.NamedTemporaryFile(delete=False)
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
