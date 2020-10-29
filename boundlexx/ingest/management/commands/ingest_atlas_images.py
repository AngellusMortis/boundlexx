import os
import shutil
import tempfile
import zipfile

import djclick as click
import requests
from django.core.files.base import ContentFile

from boundlexx.boundless.models import World

BASE_DIR = "/tmp/maps"


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

    for root, _, files in os.walk(BASE_DIR):
        with click.progressbar(files) as pbar:
            for name in pbar:
                world_id = int(name.split("_")[1])
                world = World.objects.get(id=world_id)
                with open(os.path.join(root, name), "rb") as atlas_image:
                    image = ContentFile(atlas_image.read())
                    image.name = f"{world_id}.png"

                    world.atlas_image = image
                    world.save()

    click.echo("Cleaning up...")
    os.remove(atlas_zip_file.name)
    shutil.rmtree(BASE_DIR)
