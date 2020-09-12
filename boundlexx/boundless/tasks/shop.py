import hashlib
from collections import namedtuple
from typing import Dict, List

from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from boundlexx.boundless.client import HTTP_ERRORS, BoundlessClient
from boundlexx.boundless.client import World as SimpleWorld
from boundlexx.boundless.models import (
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
LAST_UPDATE_PRICES = "boundless:update_prices_last"


@app.task
def try_update_prices():
    lock = cache.lock(UPDATE_PRICES_LOCK)

    do_run = True
    if lock.locked():
        last_run = cache.get(LAST_UPDATE_PRICES)
        if last_run is None:
            logger.warning("update_prices task has not ran recently, breaking lock")
            lock.reset()
        else:
            do_run = False
            logger.warning("Could not update prices, task already running")

    if do_run:
        logger.info("Starting update_prices task")
        update_prices.delay()


@app.task
def update_prices():
    lock = cache.lock(UPDATE_PRICES_LOCK)

    acquired = lock.acquire(blocking=True, timeout=1)

    if acquired:
        cache.set(LAST_UPDATE_PRICES, timezone.now(), timeout=28800)
        try:
            _update_prices()
        finally:
            lock.release()
    else:
        raise Exception("Could not update prices, task already running")


def _get_ranks(item, rank_klass, all_worlds):
    ranks: Dict[str, ItemRank] = {}
    worlds: List[SimpleWorld] = []

    now = timezone.now()

    for world in all_worlds:
        rank, _ = rank_klass.objects.get_or_create(item=item, world=world)
        if rank.next_update < now:
            ranks[world.name] = rank
            worlds.append(SimpleWorld(world.name, world.api_url))

    return ranks, worlds


def _create_item_prices(shops, price_klass, world_name, item):
    shops = sorted(
        shops,
        key=lambda s: f"{s.location.x},{s.location.y},{s.location.z}",
    )

    total = 0
    state_hash = hashlib.sha512()
    for shop in shops:
        item_price = price_klass.objects.create_from_shop_item(world_name, item, shop)

        state_hash.update(item_price.state_hash)
        total += 1

    return total, state_hash


def _update_item_prices(item, rank_klass, client_method, price_klass, all_worlds):

    client = BoundlessClient()
    ranks, worlds = _get_ranks(item, rank_klass, all_worlds)

    if len(ranks) == 0:
        return -1

    total = 0
    shops = getattr(client, client_method)(item.game_id, worlds=worlds)

    # set all existing price records to inactive
    price_klass.objects.filter(
        item=item, active=True, world__name__in=list(ranks.keys())
    ).update(active=False)

    for world_name, shops in shops.items():
        item_total, state_hash = _create_item_prices(
            shops, price_klass, world_name, item
        )
        total += item_total

        digest = str(state_hash.hexdigest())
        rank = ranks[world_name]
        if rank.state_hash != "":
            if rank.state_hash == digest:
                rank.decrease_rank()
            else:
                rank.increase_rank()

        rank.state_hash = digest
        rank.last_update = timezone.now()
        rank.save()

    return total


def _log_worlds(all_worlds):
    worlds = []
    for world in all_worlds:
        worlds.append((world.name, world.api_url))

    logger.info("All worlds: %s", worlds)


def _update_prices():
    items = Item.objects.filter(active=True)
    logger.info("Updating the prices for %s items", len(items))

    all_worlds = list(
        World.objects.filter(active=True, is_creative=False, api_url__isnull=False)
        .filter(
            Q(end__isnull=True)
            | Q(
                is_locked=False,
                end__isnull=False,
                end__gt=timezone.now(),
                owner__isnull=False,
            )
        )
        .exclude(api_url="")
    )
    _log_worlds(all_worlds)

    errors_total = 0

    for item in items:
        try:
            buy_updated = _update_item_prices(
                item,
                ItemBuyRank,
                "shop_buy",
                ItemRequestBasketPrice,
                all_worlds,
            )
        except HTTP_ERRORS as ex:
            errors_total += 1
            buy_updated = -2
            logger.error("%s while uploading buy prices of %s", ex, item)

        try:
            sell_updated = _update_item_prices(
                item, ItemSellRank, "shop_sell", ItemShopStandPrice, all_worlds
            )
        except HTTP_ERRORS as ex:
            errors_total += 1
            sell_updated = -2
            logger.error("%s while uploading sell prices of %s", ex, item)

        if buy_updated >= -1 or sell_updated >= -1:
            if buy_updated == -1 and sell_updated == -1:
                logger.info("Skipped %s", item)
            else:

                def status(v):
                    return v if v >= 0 else "skipped" if v == -1 else "error"

                logger.info(
                    "Updated %s (Baskets: %s, Stands: %s)",
                    item,
                    status(buy_updated),
                    status(sell_updated),
                )

        if errors_total > 10:
            raise Exception("Aborting due to large number of HTTP errors")
