import djclick as click
import requests
from django.core.files.base import ContentFile

from boundlexx.boundless.models import World
from boundlexx.utils import make_thumbnail


@click.command()
@click.argument("world_id", nargs=1, type=int)
@click.argument("image_url", nargs=1)
def command(world_id, image_url):
    world = World.objects.get(pk=world_id)
    response = requests.get(image_url)

    response.raise_for_status()

    image = ContentFile(response.content)
    image.name = f"{world.id}.png"

    if world.image is not None and world.image.name:
        world.image.delete()

    if world.image_small is not None and world.image_small.name:
        world.image_small.delete()

    world.image = image
    world.image_small = make_thumbnail(image)
    world.save()
