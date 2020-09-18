import djclick as click

from boundlexx.boundless.models import World
from boundlexx.notifications.models import ExoworldNotification


@click.command()
@click.argument("world_id", type=int)
def command(world_id):
    try:
        world = World.objects.get(id=world_id)
    except World.DoesNotExist:
        click.secho("World not found!", fg="red")

    wp = world.worldpoll_set.all().order_by("time").first()

    if wp is None:
        click.secho("No world polls!", fg="red")

    click.echo(ExoworldNotification().forum(world, wp.resources))
