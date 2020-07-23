import hashlib
from collections import namedtuple
from typing import Dict

from celery.utils.log import get_task_logger
from django.utils import timezone
from django.core.cache import cache

from bge.boundless.client import BoundlessClient
from bge.boundless.models import (
    Item,
    ItemBuyRank,
    ItemRank,
    ItemRequestBasketPrice,
    ItemSellRank,
    ItemShopStandPrice,
    World,
)
from config.celery_app import app

logger = get_task_logger(__name__)


UpdateOption = namedtuple(
    "UpdateOption", ("rank_klass", "client_method", "price_klass")
)


UPDATE_PRICES_LOCK = "boundless:update_prices"


@app.task
def try_update_prices():
    lock = cache.lock(UPDATE_PRICES_LOCK)

    acquired = lock.acquire(blocking=True, timeout=1)

    if acquired:
        try:
            _update_prices()
        finally:
            lock.release()
    else:
        logger.warning("Could not update prices, task already running")


def _update_prices():
    items = Item.objects.filter(active=True)
    client = BoundlessClient()

    logger.info("Updating the prices for %s items", len(items))

    all_worlds = list(World.objects.filter(active=True, is_perm=True))
    for item in items:
        options = {
            "buy": UpdateOption(
                ItemBuyRank, "shop_buy", ItemRequestBasketPrice,
            ),
            "sell": UpdateOption(
                ItemSellRank, "shop_sell", ItemShopStandPrice,
            ),
        }

        totals = {"buy": 0, "sell": 0}

        updated = False
        for option_name, option in options.items():
            ranks: Dict[str, ItemRank] = {}
            now = timezone.now()
            for world in all_worlds:
                rank, _ = option.rank_klass.objects.get_or_create(
                    item=item, world=world
                )
                if rank.next_update < now:
                    ranks[world.name] = rank

            if len(ranks) > 0:
                updated = True

                shops = getattr(client, option.client_method)(
                    item.game_id, worlds=list(ranks.keys())
                )

                option.price_klass.objects.filter(
                    item=item, active=True
                ).update(active=False)

                for world_name, shops in shops.items():
                    state_hash = hashlib.sha512()

                    shops = sorted(shops, key=lambda s: s.location)
                    for shop in shops:
                        item_price = option.price_klass.from_shop_item(
                            world_name, item, shop
                        )

                        state_hash.update(item_price.state_hash)
                        totals[option_name] += 1

                    digest = str(state_hash.hexdigest())
                    rank = ranks[world_name]
                    if rank.state_hash == digest:
                        rank.decrease_rank()
                    elif rank.rank > 5:
                        rank.rank = 5
                    else:
                        rank.increase_rank()

                    rank.state_hash = digest
                    rank.last_update = timezone.now()
                    rank.save()

        if updated:
            logger.info(
                "Updated %s (Baskets: %s, Stands: %s)",
                item,
                totals["buy"],
                totals["sell"],
            )
        else:
            logger.info("Skipped %s", item)


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
