import djclick as click

from boundlexx.boundless.models import WorldBlockColor


@click.command()
def command():
    WorldBlockColor.objects.all().update(
        _new_color=None,
        _exist_on_perm=None,
        _exist_via_transform=None,
        _days_since_last=None,
    )

    with click.progressbar(WorldBlockColor.objects.order_by("world_id")) as pbar:
        for block_color in pbar:
            block_color.exist_on_perm  # pylint: disable=pointless-statement
            block_color.is_new_color  # pylint: disable=pointless-statement
            block_color.exist_via_transform  # noqa: E501  # pylint: disable=pointless-statement
            block_color.days_since_last  # pylint: disable=pointless-statement
