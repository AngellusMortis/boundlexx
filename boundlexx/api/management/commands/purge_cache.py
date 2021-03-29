import djclick as click

from boundlexx.api.tasks import purge_cache, purge_static_cache


@click.command()
def command():
    click.echo("Purging static files...")
    purge_static_cache()
    click.echo("Purging endpoints...")
    purge_cache(all_paths=True)
