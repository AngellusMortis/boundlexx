import time
from datetime import timedelta
from typing import Any, Optional

from azure.mgmt.cdn import CdnManagementClient
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from msrestazure.azure_active_directory import ServicePrincipalCredentials

from config.celery_app import app

MAX_SINGLE_PURGE = 50
CDN_PURGE_KEY = "boundless:cdn_last_purge"
ITEM_COLOR_IDS_KEYS = "boundless:resource_ids"
PURGE_CACHE_COUNT = "boundless:purge_cache_count"
PURGE_COUNT_LOCK = "boundless:purge_cache_count_lock"

logger = get_task_logger(__name__)

PURGE_GROUPS = {
    "__all__": ["/api/v1/*"],
    "World": ["/api/v1/worlds/", "/api/v1/worlds/{world_id}/*"],
    "Color": ["/api/v1/colors/", "/api/v1/colors/{color_id}/*"],
    "Item": ["/api/v1/items/", "/api/v1/items/{item_id}/*"],
    "ItemRequestBasketPrice": [
        "/api/v1/items/{item_id}/request-baskets/*",
        "/api/v1/worlds/{world_id}/request-baskets/*",
    ],
    "ItemShopStandPrice": [
        "/api/v1/items/{item_id}/shop-stands/*",
        "/api/v1/worlds/{world_id}/shop-stands/*",
    ],
    "WorldPoll": [
        "/api/v1/worlds/{world_id}/polls/*",
    ],
    "ResourceCount": [
        "/api/v1/items/{item_id}/resource-counts/*",
        "/api/v1/items/{item_id}/resource-timeseries/*",
    ],
    "WorldBlockColor": [
        "/api/v1/colors/{color_id}/blocks/*",
        "/api/v1/items/{item_id}/colors/*",
        "/api/v1/worlds/{world_id}/block-colors/*",
    ],
}


def _get_paths_world(pk):
    from boundlexx.boundless.models import World

    world = World.objects.get(pk=pk)
    paths = PURGE_GROUPS["World"]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{world_id}", str(world.id))

    return paths, f"{CDN_PURGE_KEY}:world:{world.id}"


def _get_paths_color(pk):
    from boundlexx.boundless.models import Color

    color = Color.objects.get(pk=pk)
    paths = PURGE_GROUPS["Color"]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{color_id}", str(color.game_id))

    return paths, f"{CDN_PURGE_KEY}:color:{color.game_id}"


def _get_paths_item(pk):
    from boundlexx.boundless.models import Item

    item = Item.objects.get(pk=pk)
    paths = PURGE_GROUPS["Item"]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{item_id}", str(item.game_id))

    return paths, f"{CDN_PURGE_KEY}:item:{item.game_id}"


def _get_paths_shop_stand(pk):
    from boundlexx.boundless.models import ItemShopStandPrice

    shop = ItemShopStandPrice.objects.select_related("item", "world").get(
        pk=pk
    )
    paths = PURGE_GROUPS["ItemShopStandPrice"]

    for index, path in enumerate(paths):
        path = path.replace("{item_id}", str(shop.item.game_id))
        paths[index] = path.replace("{world_id}", str(shop.world.id))

    return (
        paths,
        (
            f"{CDN_PURGE_KEY}:shop-stand:"
            f"{shop.world.id}:{shop.item.game_id}"
        ),
    )


def _get_paths_request_basket(pk):
    from boundlexx.boundless.models import ItemRequestBasketPrice

    shop = ItemRequestBasketPrice.objects.select_related("item", "world").get(
        pk=pk
    )
    paths = PURGE_GROUPS["ItemRequestBasketPrice"]

    for index, path in enumerate(paths):
        path = path.replace("{item_id}", str(shop.item.game_id))
        paths[index] = path.replace("{world_id}", str(shop.world.id))

    return (
        paths,
        (
            f"{CDN_PURGE_KEY}:request-basket:"
            f"{shop.world.id}:{shop.item.game_id}"
        ),
    )


def _get_paths_world_poll(pk):
    from boundlexx.boundless.models import WorldPoll

    poll = WorldPoll.objects.select_related("world").get(pk=pk)
    paths = PURGE_GROUPS["WorldPoll"]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{world_id}", str(poll.world.id))

    return paths, f"{CDN_PURGE_KEY}:world-poll:{poll.world.id}"


def _get_paths_resouce_count(pk):
    from boundlexx.boundless.models import ResourceCount

    count = ResourceCount.objects.select_related("item").get(pk=pk)
    paths = PURGE_GROUPS["ResourceCount"]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{item_id}", str(count.item.game_id))

    return paths, f"{CDN_PURGE_KEY}:resource-count:{count.item.game_id}"


def _get_paths_block_color(pk):
    from boundlexx.boundless.models import WorldBlockColor

    block_color = WorldBlockColor.objects.select_related(
        "item", "world", "color"
    ).get(pk=pk)
    paths = PURGE_GROUPS["WorldBlockColor"]

    for index, path in enumerate(paths):
        path = path.replace("{item_id}", str(block_color.item.game_id))
        path = path.replace("{world_id}", str(block_color.world.id))
        paths[index] = path.replace(
            "{color_id}", str(block_color.color.game_id)
        )

    return (
        paths,
        (
            f"{CDN_PURGE_KEY}:block_color:"
            f"{block_color.world.id}:{block_color.item.game_id}:"
            f"{block_color.color.game_id}"
        ),
    )


def _get_paths(model_name: Optional[str] = None, pk: Optional[Any] = None):
    paths = []
    cache_key = None

    if model_name is None:
        paths = PURGE_GROUPS["__all__"]
        cache_key = f"{CDN_PURGE_KEY}:all"

    if model_name == "World":
        paths, cache_key = _get_paths_world(pk)

    if model_name == "Color":
        paths, cache_key = _get_paths_color(pk)

    if model_name == "Item":
        paths, cache_key = _get_paths_item(pk)

    if model_name == "ItemShopStandPrice":
        paths, cache_key = _get_paths_shop_stand(pk)

    if model_name == "ItemRequestBasketPrice":
        paths, cache_key = _get_paths_request_basket(pk)

    if model_name == "WorldPoll":
        paths, cache_key = _get_paths_world_poll(pk)

    if model_name == "ResourceCount":
        paths, cache_key = _get_paths_resouce_count(pk)

    if model_name == "WorldBlockColor":
        paths, cache_key = _get_paths_block_color(pk)

    return paths, cache_key


def _path_chunks(iterable, chunk_size):
    while len(iterable) > chunk_size:
        yield iterable[:chunk_size]
        iterable = iterable[chunk_size:]
    yield iterable


def _purge_paths(client, paths):
    _add_to_count(len(paths))

    try:
        logger.info("Purging paths: %s", paths)
        poller = client.endpoints.purge_content(
            settings.AZURE_CDN_RESOURCE_GROUP,
            settings.AZURE_CDN_PROFILE_NAME,
            settings.AZURE_CDN_ENDPOINT_NAME,
            paths,
        )
        poller.result()
    finally:
        _remove_from_count(len(paths))


def _add_to_count(count):
    success = False

    while not success:
        with cache.lock(PURGE_COUNT_LOCK, expire=10, auto_renewal=False):
            in_progress_count = cache.get(PURGE_CACHE_COUNT, 0)
            in_progress_count += count

            if in_progress_count <= MAX_SINGLE_PURGE:
                logger.info(
                    "Incrementing in progress count: %s", in_progress_count
                )
                cache.set(PURGE_CACHE_COUNT, in_progress_count, timeout=600)
                success = True
        # do not sleep with lock
        if not success:
            time.sleep(1)


def _remove_from_count(count):
    with cache.lock(PURGE_COUNT_LOCK, expire=10, auto_renewal=False):
        in_progress_count = cache.get(PURGE_CACHE_COUNT, 0)
        in_progress_count -= count

        if in_progress_count < 0:
            logger.error("In progress count is less than 0")
            in_progress_count = 0

        logger.info("Decrementing in progress count: %s", in_progress_count)
        cache.set(PURGE_CACHE_COUNT, in_progress_count, timeout=600)


@app.task
def purge_cache(model_name: Optional[str] = None, pk: Optional[Any] = None):
    logger.info("Purging cache for %s (%s)", model_name, pk)

    if (
        settings.AZURE_CDN_ENDPOINT_NAME is None
        or len(settings.AZURE_CDN_ENDPOINT_NAME) == 0
    ):
        logger.warning("Azure settings not configured")
        return

    paths, cache_key = _get_paths(model_name, pk)
    if len(paths) == 0:
        logger.warning("No paths to purge")
        return

    next_purge = cache.get(cache_key)
    now = timezone.now()

    if next_purge is not None and now <= next_purge:
        logger.info("Skipping purge, already purged recently (%s)", cache_key)
        return

    credentials = ServicePrincipalCredentials(
        settings.AZURE_CLIENT_ID,
        settings.AZURE_CLIENT_SECRET,
        tenant=settings.AZURE_TENANT_ID,
    )

    client = CdnManagementClient(credentials, settings.AZURE_SUBSCRIPTION_ID)

    for paths_group in _path_chunks(paths, MAX_SINGLE_PURGE):
        _purge_paths(client, paths_group)

    next_purge = timezone.now() + timedelta(minutes=1)
    cache.set(cache_key, next_purge, timeout=60)
