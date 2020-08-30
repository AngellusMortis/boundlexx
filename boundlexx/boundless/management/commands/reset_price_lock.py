import djclick as click
from django.core.cache import cache

from boundlexx.boundless.tasks.shop import UPDATE_PRICES_LOCK


@click.command()
def command():
    cache.delete(UPDATE_PRICES_LOCK)
