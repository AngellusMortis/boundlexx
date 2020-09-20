import djclick as click

from boundlexx.boundless.tasks import recalculate_colors


@click.command()
@click.argument("world_id", nargs=1, required=False)
def command(world_id=None):
    if world_id is None:
        recalculate_colors(None, log=click.echo)
    else:
        recalculate_colors([world_id], log=click.echo)
