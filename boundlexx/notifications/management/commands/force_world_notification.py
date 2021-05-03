import os

import djclick as click

from boundlexx.boundless.models import World
from boundlexx.notifications.models import ExoworldNotification


@click.command()
@click.argument("world_id", type=int)
@click.option("-u", "--update", is_flag=True)
def command(world_id, update):
    try:
        world = World.objects.get(id=world_id)
    except World.DoesNotExist:
        click.secho("World not found!", fg="red")

    os.environ["NOTIFICATION_PRINT"] = "1"
    if update:
        world.notification_sent = False
        world.save()
        ExoworldNotification.objects.send_update_notification(world)
    else:
        wp = world.worldpoll_set.all().order_by("time").first()

        if wp is None:
            click.secho("No world polls!", fg="red")

        ExoworldNotification.objects.send_new_notification(wp)
