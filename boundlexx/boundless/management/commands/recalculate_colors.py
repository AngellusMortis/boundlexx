import djclick as click

from boundlexx.boundless.models import WorldBlockColor


@click.command()
def command():
    WorldBlockColor.objects.all().update(
        _exist_on_perm=None,
        _sovereign_only=None,
        _new_color=None,
        _new_exo_color=None,
        _via_transform_world=None,
        _exist_via_transform=None,
        _via_exo_transform_world=None,
        _exist_via_exo_transform=None,
        _last_exo_world=None,
        _days_since_last_exo=None,
    )

    wbcs = WorldBlockColor.objects.order_by("world_id")
    with click.progressbar(wbcs, show_percent=True, show_pos=True) as pbar:
        for block_color in pbar:
            block_color.exist_on_perm  # pylint: disable=pointless-statement
            block_color.sovereign_only  # pylint: disable=pointless-statement
            block_color.is_new_color  # noqa: E501  # pylint: disable=pointless-statement
            block_color.is_new_exo_color  # pylint: disable=pointless-statement
            block_color.exist_via_transform  # pylint: disable=pointless-statement
            block_color.exist_via_exo_transform  # pylint: disable=pointless-statement
            block_color.days_since_last_exo  # pylint: disable=pointless-statement
