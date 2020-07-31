import djclick as click

from boundlexx.boundless.utils import purge_cache


@click.command()
def command():
    purge_cache()
