import djclick as click
from django.core.cache import cache

from boundlexx.api.tasks import purge_cache, purge_static_cache
from boundlexx.boundless.utils import (
    ITEM_COLOR_IDS_KEYS,
    ITEM_METAL_IDS_KEYS,
    WORLD_ITEM_COLOR_IDS_KEYS,
)


@click.command()
def command():
    click.echo("Purging redis caches...")
    cache.delete(ITEM_COLOR_IDS_KEYS)
    cache.delete(WORLD_ITEM_COLOR_IDS_KEYS)
    cache.delete(ITEM_METAL_IDS_KEYS)
    click.echo("Purging static files...")
    purge_static_cache()
    click.echo("Purging endpoints...")
    purge_cache(all_paths=True)
