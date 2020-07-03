import json

import djclick as click

from bge.boundless.models import Item


@click.command()
@click.argument("itemsmapping", type=click.File())
def command(itemsmapping):
    items = json.load(itemsmapping)

    click.echo(f"Found {len(items)} items")

    created = 0
    for item_dict in items.values():
        _, was_created = Item.objects.get_or_create(
            name=item_dict["name"],
            id=item_dict["id"],
            gui_name=item_dict["guiname"],
        )

        if was_created:
            created += 1

    if created > 0:
        click.echo(f"Imported {created} new item(s)")
    else:
        click.echo("No new items to import")
