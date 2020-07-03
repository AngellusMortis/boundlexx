from celery.utils.log import get_task_logger

from bge.boundless.client import BoundlessClient
from bge.boundless.models import (
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
)
from config.celery_app import app

logger = get_task_logger(__name__)


@app.task
def update_prices():
    items = Item.objects.filter(active=True)
    client = BoundlessClient()

    logger.info("Updating the prices for %s", len(items))

    for item in items:
        total_baskets = 0
        total_stands = 0

        request_baskets = client.shop_buy(item.id)
        for world, baskets in request_baskets.items():
            for basket in baskets:
                ItemRequestBasketPrice.from_shop_item(world, item, basket)
                total_baskets += 1

        shop_stands = client.shop_sell(item.id)
        for world, stands in shop_stands.items():
            for stand in stands:
                ItemShopStandPrice.from_shop_item(world, item, stand)
                total_stands += 1

        logger.info(
            "Updated %s (Baskets: %s, Stands: %s)",
            item.gui_name,
            total_baskets,
            total_stands,
        )
