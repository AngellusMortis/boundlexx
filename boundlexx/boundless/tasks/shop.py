import hashlib
import re
from ast import literal_eval
from collections import namedtuple
from datetime import timedelta
from typing import Dict, List

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django_celery_results.models import TaskResult

from boundlexx.boundless.client import HTTP_ERRORS, BoundlessClient
from boundlexx.boundless.client import World as SimpleWorld
from boundlexx.boundless.models import (
    Color,
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
WORLDS_QUEUED_LOCK = "boundless:prices:update_worlds"
WORLDS_QUEUED_CACHE = "boundless:prices:worlds"
UPDATE_PRICES_TASK = "boundlexx.boundless.tasks.shop.update_prices_split"


def _get_queued_worlds():
    logger.info("Getting queued worlds lock (get)...")
    with cache.lock(WORLDS_QUEUED_LOCK):
        queued_worlds = list(cache.get(WORLDS_QUEUED_CACHE, set()))
        logger.info("Releasing queued worlds lock (get)...")
    return queued_worlds


def _update_queued_worlds(worlds):
    actual_worlds = []
    logger.info("Getting queued worlds lock (update)...")
    with cache.lock(WORLDS_QUEUED_LOCK):
        in_progress_ids = cache.get(WORLDS_QUEUED_CACHE, set())

        for world in worlds:
            if world.id not in in_progress_ids:
                in_progress_ids.add(world.id)
                actual_worlds.append(world)

        logger.info("Added queued worlds: %s", [w.id for w in actual_worlds])
        logger.info("Set queued worlds (update): %s", in_progress_ids)
        cache.set(WORLDS_QUEUED_CACHE, in_progress_ids, timeout=21600)
        logger.info("Releasing queued worlds lock (update)...")

    return actual_worlds


def _remove_queued_worlds(world_ids):
    logger.info("Getting queued worlds lock (remove)...")
    with cache.lock(WORLDS_QUEUED_LOCK):
        logger.info("Removing queued worlds: %s", world_ids)
        in_progress_ids = cache.get(WORLDS_QUEUED_CACHE, set())

        for world_id in world_ids:
            in_progress_ids.discard(world_id)

        logger.info("Set queued worlds (remove): %s", in_progress_ids)
        cache.set(WORLDS_QUEUED_CACHE, in_progress_ids, timeout=21600)
        logger.info("Releasing queued worlds lock (remove)...")


@app.task
def update_prices(world_ids=None):
    queued_ids = _get_queued_worlds()

    if world_ids is None:
        worlds = (
            World.objects.filter(
                active=True,
                is_creative=False,
                api_url__isnull=False,
                is_public=True,
            )
            .filter(
                Q(end__isnull=True)
                | Q(
                    is_locked=False,
                    end__isnull=False,
                    end__gt=timezone.now(),
                    owner__isnull=False,
                    start__lte=timezone.now() - timedelta(hours=12),
                )
            )
            .exclude(api_url="")
            .exclude(id__in=queued_ids)
        )
    else:
        worlds = World.objects.filter(id__in=world_ids).order_by("id")

    if worlds.count() == 0:
        logger.info("No worlds to update")
        return

    _update_prices_multi(worlds)


@app.task
def update_prices_split(world_ids):
    worlds = World.objects.filter(id__in=world_ids).order_by("id")

    first = worlds.first()

    if first is None:
        return

    count = worlds.count()

    _update_prices_multi(worlds, f"{first.id}:{count}")


def _update_prices_multi(worlds, name=None):
    lock_name = UPDATE_PRICES_LOCK

    if name is not None:
        lock_name = f"{lock_name}:{name}"

    lock = cache.lock(lock_name, expire=120, auto_renewal=False)

    acquired = lock.acquire(blocking=True, timeout=1)

    if not acquired:
        return

    try:
        _update_prices(worlds)
    finally:
        try:
            lock.release()
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("Could not release lock: %s", ex)


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

    colors = Color.objects.all()

    total = 0
    state_hash = hashlib.sha512()
    for shop in shops:
        item_price = price_klass.objects.create_from_shop_item(
            world_name, item, shop, colors=colors
        )

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


def _split_update_prices(worlds):
    max_sov_worlds = settings.BOUNDLESS_MAX_SOV_WORLDS_PER_PRICE_POLL
    max_perm_worlds = settings.BOUNDLESS_MAX_PERM_WORLDS_PER_PRICE_POLL

    worlds = list(worlds)
    run = 1
    while len(worlds) > max_sov_worlds or (
        len(worlds) > 1 and worlds[0].is_perm and len(worlds) > max_perm_worlds
    ):
        max_worlds = max_sov_worlds
        if worlds[0].is_perm:
            max_worlds = max_perm_worlds

        worlds_ids = [w.id for w in worlds[:max_worlds]]
        logger.info("Run %s: %s", run, worlds_ids)
        update_prices_split.delay(worlds_ids)
        worlds = worlds[max_worlds:]
        run += 1

    if len(worlds) > 0:
        worlds_ids = [w.id for w in worlds]
        logger.info("Run %s: %s", run, worlds_ids)
        update_prices_split.delay(worlds_ids)


def _log_result(item, buy_updated, sell_updated):
    def status(v):
        return v if v >= 0 else "skipped" if v == -1 else "error"

    if buy_updated >= -1 or sell_updated >= -1:
        if buy_updated == -1 and sell_updated == -1:
            logger.info("Skipped %s", item)
        else:
            logger.info(
                "Updated %s (Baskets: %s, Stands: %s)",
                item,
                status(buy_updated),
                status(sell_updated),
            )


def _check_split(worlds):
    total = len(worlds)

    first_world = worlds[0]

    if first_world.is_perm:
        if total > settings.BOUNDLESS_MAX_PERM_WORLDS_PER_PRICE_POLL:
            _split_update_prices(worlds)
            return True
    elif first_world.is_sovereign:
        if total > settings.BOUNDLESS_MAX_SOV_WORLDS_PER_PRICE_POLL:
            _split_update_prices(worlds)
            return True

    return False


def _remove_world(ex, worlds):
    world = None
    match = re.match(r"playboundless\.com/(\d+)/api", str(ex))
    if match is not None:
        world = [w for w in worlds if w.id == int(match.group(1))][0]

    if world is None:
        logger.warning(
            "World not found, but could not find world ID",
        )
    else:
        world = [w for w in worlds if w.id == int(match.group(1))][0]

        logger.warning(
            "World (%s) not found, removing from list of worlds to query",
            world,
        )
        worlds.remove(world)

    return worlds


def _update_prices(worlds):
    worlds = list(worlds)
    did_split = _check_split(worlds)

    if did_split:
        return

    worlds = _update_queued_worlds(worlds)

    if len(worlds) == 0:
        logger.info("No worlds to update")
        return

    ids_to_remove = [w.id for w in worlds]
    items = Item.objects.filter(active=True, can_be_sold=True)
    logger.info("Updating the prices for %s items", len(items))

    _log_worlds(worlds)

    errors_total = 0

    try:
        for item in items:
            buy_updated, sell_updated = -1, -1

            try:
                buy_updated = _update_item_prices(
                    item,
                    ItemBuyRank,
                    "shop_buy",
                    ItemRequestBasketPrice,
                    worlds,
                )
            except HTTP_ERRORS as ex:
                response_code = None

                if hasattr(ex, "response") and ex.response is not None:  # type: ignore
                    response_code = ex.response.status_code  # type: ignore

                if response_code == 404:
                    worlds = _remove_world(ex, worlds)

                # 403 with an API key can actually be a rate limit...
                elif not response_code == 403:
                    errors_total += 1
                    buy_updated = -2
                    logger.error("%s while updating buy prices of %s", ex, item)

            try:
                sell_updated = _update_item_prices(
                    item, ItemSellRank, "shop_sell", ItemShopStandPrice, worlds
                )
            except HTTP_ERRORS as ex:
                # 403 with an API key can actually be a rate limit...
                if not (
                    hasattr(ex, "response")
                    and ex.response is not None  # type: ignore
                    and ex.response.status_code == 403  # type: ignore
                ):
                    errors_total += 1
                    sell_updated = -2
                    logger.error("%s while updating sell prices of %s", ex, item)

            _log_result(item, buy_updated, sell_updated)
            if errors_total > 10:
                raise Exception("Aborting due to large number of HTTP errors")
    finally:
        _remove_queued_worlds(ids_to_remove)


@app.task
def clean_up_queued_worlds():
    logger.info("Getting queued worlds lock (clean)...")
    with cache.lock(WORLDS_QUEUED_LOCK):
        cached_queued_worlds = cache.get(WORLDS_QUEUED_CACHE, set())
        in_progress_tasks = TaskResult.objects.filter(
            task_name=UPDATE_PRICES_TASK, status="STARTED"
        )
        logger.info("Releasing queued worlds lock (clean)...")

    actual_queued_worlds = set()
    for task in in_progress_tasks:
        world_ids: List[int] = literal_eval(task.task_args)[0]
        for world_id in world_ids:
            if world_id in actual_queued_worlds:
                logger.warning("Duplicate world ID found!")
            actual_queued_worlds.add(world_id)

    old_queued_worlds = cached_queued_worlds - actual_queued_worlds

    _remove_queued_worlds(list(old_queued_worlds))
