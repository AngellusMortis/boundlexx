import djclick as click

from boundlexx.boundless.models import Item, LocalizedString
from boundlexx.ingest.models import GameFile


def run():
    click.echo("Attaching localization data to items...")
    compiled_items = GameFile.objects.get(
        folder="assets/archetypes", filename="compileditems.msgpack"
    ).content
    with click.progressbar(Item.objects.all()) as pbar:
        for item in pbar:
            list_type = compiled_items[str(item.game_id)].get("listTypeName")

            if list_type:
                item.list_type = LocalizedString.objects.filter(
                    string_id=list_type
                ).first()
            item.description = LocalizedString.objects.filter(
                string_id=f"{item.string_id}_DESCRIPTION"
            ).first()
            item.save()
