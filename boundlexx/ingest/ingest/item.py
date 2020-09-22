import djclick as click

from boundlexx.boundless.models import AltItem, Block, Item, LocalizedString
from boundlexx.ingest.models import GameFile


def run():
    items = {}

    compiled_items = GameFile.objects.get(
        folder="assets/archetypes", filename="compileditems.msgpack"
    ).content

    click.echo("Attaching localization data to items...")
    with click.progressbar(Item.objects.all()) as pbar:
        for item in pbar:
            items[item.game_id] = item
            list_type = compiled_items[str(item.game_id)].get("listTypeName")

            if list_type:
                item.list_type = LocalizedString.objects.filter(
                    string_id=list_type
                ).first()
            item.description = LocalizedString.objects.filter(
                string_id=f"{item.string_id}_DESCRIPTION"
            ).first()
            item.save()

    click.echo("Creating AltItems...")
    with click.progressbar(compiled_items.items()) as pbar:
        for item_id, item_data in pbar:
            item_id = int(item_id)

            if item_id in items:
                continue

            string_id = item_data["stringID"]
            if "ITEM_TYPE_ASH_RECLAIM" in string_id:
                string_id = "ITEM_TYPE_ASH_DEFAULT_BASE"

            item = Item.objects.filter(string_id=string_id).first()

            if item is not None:
                alt_item, _ = AltItem.objects.get_or_create(
                    game_id=int(item_data["id"]), name=item_data["name"], base_item=item
                )

                items[alt_item.game_id] = item

    click.echo("Generating block mappings...")
    compiled_blocks = GameFile.objects.get(
        folder="assets/archetypes", filename="compiledblocks.msgpack"
    ).content
    blocks_created = 0
    with click.progressbar(compiled_blocks["BlockTypesData"]) as pbar:
        for block_data in pbar:
            if block_data is None:
                continue

            item = None
            item_id = (
                block_data["inventoryRemap"]
                or block_data["rootType"]
                or block_data["id"]
            )
            if item_id != 0:
                item = items.get(item_id)

            if item is None:
                item = Item.objects.filter(
                    string_id=f"ITEM_TYPE_{block_data['name']}"
                ).first()

            _, created = Block.objects.get_or_create(
                game_id=block_data["id"], name=block_data["name"], block_item=item
            )

            if created:
                blocks_created += 1

    click.echo(f"{blocks_created} Block(s) created")
