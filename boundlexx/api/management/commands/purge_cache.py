import djclick as click

from boundlexx.api.tasks import purge_cache


@click.command()
def command():
    purge_cache()
