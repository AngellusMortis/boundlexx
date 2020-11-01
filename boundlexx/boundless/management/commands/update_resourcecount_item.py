import djclick as click

from boundlexx.boundless.models import Item, ResourceCount

ITEM_UPDATE_MAP = {
    32800: 13620,  # Rough Amethyst
    32803: 13624,  # Rough Diamond
    32804: 13628,  # Rough Emerald
    32809: 13632,  # Rough Topaz
    32807: 13636,  # Rough Ruby
    32808: 13640,  # Rough Sapphire
    32806: 13644,  # Rough Rift
    32801: 13648,  # Rough Blink
    32785: 13652,  # Copper Ore
    32787: 13656,  # Iron Ore
    32788: 13660,  # Silver Ore
    32786: 13664,  # Gold Ore
    32789: 13668,  # Titanium Ore
    32779: 13672,  # Soft Coal
    32777: 13676,  # Medium Coal
    32778: 13680,  # Hard Coal
    33081: 13684,  # Small Fossil
    33082: 13688,  # Medium Fossil
    33083: 13692,  # Large Fossil
    33080: 13696,  # Ancient Tech Remnant
    33078: 13700,  # Ancient Tech Component
    33079: 13704,  # Ancient Tech Device
    32802: 13708,  # Rough Umbris
    32805: 13712,  # Rough Oortstone
}


@click.command()
def command():
    for from_id, to_id in ITEM_UPDATE_MAP.items():
        from_item = Item.objects.get(game_id=from_id)
        to_item = Item.objects.get(game_id=to_id)

        click.echo(f"Updating {from_item} to {to_item} in Resource Counts...")

        ResourceCount.objects.filter(item_id=from_item.id).update(item_id=to_item.id)
