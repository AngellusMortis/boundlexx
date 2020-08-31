import djclick as click

from boundlexx.boundless.models import ItemBuyRank, ItemSellRank


@click.command()
def command():
    ItemBuyRank.objects.all().delete()
    ItemSellRank.objects.all().delete()
