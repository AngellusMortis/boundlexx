import djclick as click

from boundlexx.boundless.models import Color, World
from boundlexx.boundless.utils import calculate_extra_names


@click.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Clear existing",
)
def command(force):
    if force:
        World.objects.all().update(text_name=None, html_name=None, sort_name=None)

    colors = Color.objects.all()

    worlds = World.objects.all()
    with click.progressbar(
        worlds.iterator(), length=worlds.count(), show_percent=True, show_pos=True
    ) as pbar:
        for world in pbar:
            world = calculate_extra_names(world, world.display_name, colors=colors)
            world.save()
