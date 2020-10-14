import djclick as click

from boundlexx.boundless.models import ResourceCount, World


def _fix_resource(resource):
    kwargs = {
        "time": resource.world_poll.time,
        "world_poll": resource.world_poll,
        "item": resource.item,
        "count": resource.count,
        "percentage": resource.percentage,
        "average_per_chunk": resource.count / pow(resource.world_poll.world.size, 2),
        "fixed_average": True,
    }

    resource.delete()

    ResourceCount.objects.filter(
        world_poll=kwargs["world_poll"], item=kwargs["item"]
    ).delete()

    ResourceCount.objects.create(**kwargs)


def _all(reverse):
    resources = ResourceCount.objects.filter(fixed_average=False).select_related(
        "world_poll", "item", "world_poll__world"
    )

    if reverse:
        resources = resources.order_by("world_poll_id", "item_id", "time").distinct(
            "world_poll_id", "item_id"
        )
    else:
        resources = resources.order_by("world_poll_id", "item_id", "-time").distinct(
            "world_poll_id", "item_id"
        )

    with click.progressbar(
        resources.iterator(), length=resources.count(), show_percent=True, show_pos=True
    ) as pbar:
        for resource in pbar:
            _fix_resource(resource)


def _initial():
    with click.progressbar(
        World.objects.all(), show_percent=True, show_pos=True
    ) as pbar:
        for world in pbar:
            wp = world.worldpoll_set.order_by("time").first()

            if wp is None:
                continue

            for resource in wp.resources.filter(fixed_average=False):
                _fix_resource(resource)


@click.command()
@click.option(
    "-i",
    "--initial",
    is_flag=True,
    help="Only do initial polls per world",
)
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    help="Start at begining",
)
def command(initial, reverse):
    if initial:
        _initial()
    else:
        _all(reverse)
