from celery.utils.log import get_task_logger

from bge.boundless.client import BoundlessClient
from bge.boundless.models import (
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    World,
)
from config.celery_app import app

logger = get_task_logger(__name__)


@app.task
def update_prices():
    items = Item.objects.filter(active=True)
    client = BoundlessClient()

    logger.info("Updating the prices for %s items", len(items))

    for item in items:
        total_baskets = 0
        total_stands = 0

        request_baskets = client.shop_buy(item.game_id)
        ItemRequestBasketPrice.objects.filter(item=item, active=True).update(
            active=False
        )
        for world, baskets in request_baskets.items():
            for basket in baskets:
                ItemRequestBasketPrice.from_shop_item(world, item, basket)
                total_baskets += 1

        shop_stands = client.shop_sell(item.game_id)
        ItemShopStandPrice.objects.filter(item=item, active=True).update(
            active=False
        )
        for world, stands in shop_stands.items():
            for stand in stands:
                ItemShopStandPrice.from_shop_item(world, item, stand)
                total_stands += 1

        logger.info(
            "Updated %s (Baskets: %s, Stands: %s)",
            item,
            total_baskets,
            total_stands,
        )


@app.task
def update_worlds():
    client = BoundlessClient()

    worlds = client.gameservers.values()
    logger.info("Found %s worlds from discovery server.", len(worlds))

    worlds_created = 0
    for world_dict in worlds:
        _, created = World.objects.get_or_create(
            id=world_dict["id"],
            name=world_dict["name"],
            display_name=world_dict["displayName"],
            region=world_dict["region"],
            tier=world_dict["tier"],
            description=world_dict["worldDescription"],
            size=world_dict["worldSize"],
            world_type=world_dict["worldType"],
        )

        if created:
            worlds_created += 1

    logger.info("Import %s world(s)", worlds_created)
