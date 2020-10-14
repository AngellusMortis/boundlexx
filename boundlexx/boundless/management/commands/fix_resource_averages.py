import djclick as click

from boundlexx.boundless.models import ResourceCount


@click.command()
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    help="Start at begining",
)
def command(reverse):
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
            resource.time = resource.world_poll.time
            resource.average_per_chunk = resource.count / pow(
                resource.world_poll.world.size, 2
            )
            resource.fixed_average = True
            resource.save()
