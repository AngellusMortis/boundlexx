import djclick as click

from boundlexx.boundless.models import ResourceCount


@click.command()
def command():
    resources = ResourceCount.objects.filter(
        _average_per_chunk__isnull=True
    ).select_related("world_poll", "world_poll__world")
    with click.progressbar(resources, show_percent=True, show_pos=True) as pbar:
        for resource in pbar:
            resource.average_per_chunk  # pylint: disable=pointless-statement
