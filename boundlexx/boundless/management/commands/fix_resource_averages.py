import djclick as click

from boundlexx.boundless.models import ResourceCount, World


def _fix_resource(resource):
    resource.time = resource.world_poll.time
    resource.average_per_chunk = resource.count / pow(resource.world_poll.world.size, 2)
    resource.fixed_average = True
    resource.save()


def _all(reverse):
    resources = ResourceCount.objects.filter(fixed_average=False).select_related(
        "world_poll", "world_poll__world"
    )

    if reverse:
        resources = resources.order_by("time")
    else:
        resources = resources.order_by("-time")

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

            for resource in wp.resources.all():
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
