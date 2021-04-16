import os

import djclick as click
from azure.common import AzureMissingResourceHttpError
from django.conf import settings
from requests.exceptions import HTTPError

from boundlexx.boundless.models import World
from boundlexx.utils import download_image, get_django_image_from_file, make_thumbnail


def _thumbs():
    click.echo("Adding thumbs/renmaing images...")
    duplicates = []
    worlds = World.objects.filter(image__isnull=False)
    with click.progressbar(
        worlds.iterator(), show_percent=True, show_pos=True, length=worlds.count()
    ) as pbar:
        for world in pbar:
            if world.image is not None and world.image.name:
                expected_name = f"{world.id}.png"
                if world.image.name != expected_name:
                    try:
                        temp_file = download_image(world.image.url)
                    except (AzureMissingResourceHttpError, HTTPError):
                        world.image = None
                        world.save()
                        continue
                    else:
                        world.image.delete()
                        world.image = get_django_image_from_file(
                            temp_file.name, expected_name
                        )
                    world.save()
                    world.refresh_from_db()

                    if world.image.name != expected_name:
                        duplicates.append(world.image.name)
                        continue

                if world.image_small is None or not world.image_small.name:
                    try:
                        world.image_small = make_thumbnail(world.image)
                    except AzureMissingResourceHttpError:
                        world.image = None

                expected_thumb_name = f"{world.id}_small.png"
                if world.image_small.name != expected_thumb_name:
                    try:
                        temp_file = download_image(world.image_small.url)
                    except (AzureMissingResourceHttpError, HTTPError):
                        world.image_small = None
                        world.save()
                        continue
                    else:
                        world.image_small.delete()
                        world.image_small = get_django_image_from_file(
                            temp_file.name, expected_thumb_name
                        )
                world.save()
                world.refresh_from_db()

                if world.image_small.name != expected_thumb_name:
                    duplicates.append(world.image_small.name)
                    continue

    click.echo("-----duplicates")
    click.echo(duplicates)


def _missing():
    click.echo("Fixing abandoned images...")
    not_found = []
    multiple = []
    for (dirpath, _, filenames) in os.walk(settings.BOUNDLESS_WORLDS_LOCATIONS):
        with click.progressbar(filenames, show_percent=True, show_pos=True) as pbar:
            for filename in pbar:
                world_name = filename.split(".")[0]

                if world_name.endswith("_small"):
                    os.remove(os.path.join(dirpath, filename))
                    continue

                world_name = world_name.replace("_", " ").title()

                worlds = World.objects.filter(display_name__icontains=world_name)
                if worlds.count() == 0:  # pylint: disable=no-else-continue
                    not_found.append(filename)
                    continue
                elif worlds.count() > 1:
                    multiple.append(filename)
                    continue

                world = worlds.get()
                image_path = os.path.join(dirpath, filename)
                if world.image is not None and world.image.name:
                    os.remove(image_path)
                else:
                    world.image = get_django_image_from_file(
                        image_path, f"{world.id}.png"
                    )

                    if world.image_small is not None and world.image_small.name:
                        world.image_small.delete()

                    world.image_small = make_thumbnail(world.image)
                    world.save()
                    os.remove(image_path)

    click.echo("-----not_found")
    click.echo(not_found)
    click.echo("-----multiple")
    click.echo(multiple)


@click.command()
def command():
    _thumbs()
    _missing()
