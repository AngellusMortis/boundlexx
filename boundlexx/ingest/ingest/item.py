import djclick as click

from boundlexx.boundless.models import AltItem, Block, Item, Liquid, LocalizedString
from boundlexx.ingest.models import GameFile


def _blocks(compiled_blocks, items):
    click.echo("Generating block mappings...")
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

            if item is not None:
                item.is_block = True
                item.prestige = block_data.get("prestige", 0)
                item.mine_xp = block_data.get("mineXP", 0)
                item.build_xp = block_data.get("buildXP", 0)
                item.save()

            _, created = Block.objects.get_or_create(
                game_id=block_data["id"], name=block_data["name"], block_item=item
            )

            if created:
                blocks_created += 1


def _liquids(compiled_blocks, items):
    click.echo("Generating liquid mappings...")
    liquids_created = 0
    with click.progressbar(compiled_blocks["LiquidTypesData"].values()) as pbar:
        for liquid_data in pbar:
            if liquid_data is None:
                continue

            item = None
            item_id = liquid_data["itemType"]
            if item_id != 0:
                item = items.get(item_id)

            if item is None:
                item = Item.objects.filter(
                    string_id=f"ITEM_TYPE_{liquid_data['name']}"
                ).first()

            if item is not None:
                item.is_liquid = True
                item.prestige = liquid_data.get("prestige", 0)
                item.mine_xp = liquid_data.get("mineXP", 0)
                item.build_xp = liquid_data.get("buildXP", 0)
                item.save()

            _, created = Liquid.objects.get_or_create(
                game_id=liquid_data["id"], name=liquid_data["name"], block_item=item
            )

            if created:
                liquids_created += 1

    click.echo(f"{liquids_created} Liquid(s) created")


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

    compiled_blocks = GameFile.objects.get(
        folder="assets/archetypes", filename="compiledblocks.msgpack"
    ).content

    _blocks(compiled_blocks, items)
    _liquids(compiled_blocks, items)
