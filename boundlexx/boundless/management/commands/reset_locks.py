import djclick as click
from django.core.cache import cache


@click.command()
def command():
    cache.reset_all()
