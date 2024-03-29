from __future__ import annotations

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from requests.exceptions import HTTPError

from boundlexx.boundless.game import BoundlessClient
from boundlexx.boundless.game import World as SimpleWorld
from boundlexx.boundless.models import (
    Color,
    Settlement,
    World,
    WorldDistance,
    WorldPoll,
)
from boundlexx.boundless.utils import GameErrorHandler
from boundlexx.notifications.models import ExoworldExpiredNotification
from config.celery_app import app

logger = get_task_logger(__name__)


def _get_search_ids():
    existing_worlds = World.objects.filter(
        id__lt=settings.BOUNDLESS_EXO_EXPIRED_BASE_ID,
        start__isnull=False,
        start__gt=timezone.now() - settings.BOUNDLEXX_WORLD_SEARCH_OFFSET,
    ).order_by("id")

    # no worlds with start yet, look at all worlds
    if existing_worlds.count() == 0:
        existing_worlds = World.objects.filter(
            id__lt=settings.BOUNDLESS_EXO_EXPIRED_BASE_ID
        )

    existing_ids = set()
    lowest_id = settings.BOUNDLESS_EXO_EXPIRED_BASE_ID
    highest_id = -1

    for world in existing_worlds.iterator():
        existing_ids.add(world.id)
        if world.id > highest_id:
            highest_id = world.id
        if world.id < lowest_id:
            lowest_id = world.id

    if highest_id == -1:
        logger.warning("No worlds found to use as a start")
        return None

    all_ids = set(
        range(lowest_id, highest_id + 1 + settings.BOUNDLESS_EXO_SEARCH_RADIUS)
    )

    ids_to_scan = sorted(all_ids - existing_ids)

    return ids_to_scan


@app.task
def search_new_worlds(ids_to_scan=None):
    if ids_to_scan is None:
        ids_to_scan = _get_search_ids()

        if ids_to_scan is None:
            return

    logger.info("Starting scan for new worlds (%s)", ids_to_scan)

    _, worlds = _scan_worlds(ids_to_scan)

    worlds_found = 0
    for world in worlds:
        if not world.is_perm:
            worlds_found += 1

    logger.info("Found %s exo world(s)", worlds_found)


@app.task
def discover_all_worlds(start_id=None):
    if start_id is None:
        start_id = 1

    chunks = []
    chunk_lower, chunk_upper = 0, start_id - 1
    while chunk_upper < settings.BOUNDLESS_MAX_WORLD_ID:
        chunk_lower = chunk_upper + 1
        chunk_upper = min(
            chunk_lower + settings.BOUNDLESS_MAX_SCAN_CHUNK - 1,
            settings.BOUNDLESS_MAX_WORLD_ID,
        )
        chunks.append((chunk_lower, chunk_upper))

    worlds_found = 0
    new_worlds = []
    for chunk in chunks:
        logger.info("Starting scan for worlds (%s, %s)", chunk[0], chunk[1])

        ids_to_scan = list(range(chunk[0], chunk[1] + 1))

        created, worlds = _scan_worlds(ids_to_scan)
        worlds_found += created

        new_worlds += worlds

    logger.info("Scan Complete. Found %s world(s)", worlds_found)


def _scan_worlds(ids_to_scan):
    client = BoundlessClient()
    worlds = get_worlds(ids_to_scan, client=client)

    worlds_found = 0
    world_objs = []
    for world_dict in worlds:
        poll_token = world_dict["pollData"]
        world_data = world_dict["worldData"]

        try:
            world, created = World.objects.get_or_create_from_game_dict(
                world_dict["worldData"]
            )
        except Exception:
            logger.warning(world_dict)
            raise

        if created:
            worlds_found += 1
            world_objs.append(world)

            if not world.is_locked:
                try:
                    poll_dict = client.get_world_poll(
                        SimpleWorld(
                            world_data["id"],
                            world_data["apiURL"],
                        ),
                        poll_token=poll_token,
                    )
                except HTTPError as ex:
                    if world.is_sovereign and ex.response.status_code == 400:
                        logger.warning(
                            "Could not do inital world poll world: %s",
                            world.display_name,
                        )
                        world_data = None
                    else:
                        raise

                if world_data is not None:
                    WorldPoll.objects.create_from_game_dict(
                        world_data, poll_dict, world=world, new_world=True
                    )

    logger.info("Found %s world(s)", worlds_found)

    return worlds_found, world_objs


def get_worlds(ids_to_scan, client=None):
    if client is None:
        client = BoundlessClient()

    worlds: list[dict] = []

    for world_id in ids_to_scan:
        world_data = client.get_world_data(SimpleWorld(world_id, None))

        if world_data is not None:
            worlds.append(world_data)

    return worlds


@app.task
def poll_perm_worlds():
    _poll_with_lock("perm", World.objects.filter(end__isnull=True, active=True))


@app.task
def poll_exo_worlds():
    _poll_with_lock(
        "exo", World.objects.filter(owner__isnull=True, end__isnull=False, active=True)
    )


@app.task
def poll_sovereign_worlds():
    _poll_with_lock(
        "sovereign",
        World.objects.filter(owner__isnull=False, is_creative=False, active=True),
    )


@app.task
def poll_creative_worlds():
    _poll_with_lock(
        "creative",
        World.objects.filter(owner__isnull=False, is_creative=True, active=True),
    )


@app.task
def poll_worlds(world_ids=None):
    if world_ids is None:
        # make sure perm worlds or unexpired worlds are always active
        World.objects.filter(
            Q(
                owner__isnull=True,
                end__isnull=True,
                assignment__isnull=True,
                address__isnull=False,
            )
        ).update(active=True)

        worlds = World.objects.filter(
            Q(active=True) | Q(end__isnull=False, end__gt=timezone.now())
        ).order_by("id")
    else:
        worlds = World.objects.filter(id__in=world_ids).order_by("id")

    _poll_with_lock_multi("poll", worlds)


@app.task
def poll_worlds_split(world_ids):
    worlds = World.objects.filter(id__in=world_ids).order_by("id")

    _poll_with_lock_multi("poll_split", worlds)


def _poll_with_lock_multi(name, worlds):
    first = worlds.first()

    if first is None:
        return

    count = worlds.count()
    _poll_with_lock(f"{name}:{first.id}:{count}", worlds)


def _poll_with_lock(name, worlds):
    lock = cache.lock(f"boundlexx:tasks:poll:{name}", expire=120, auto_renewal=False)

    acquired = lock.acquire(blocking=True, timeout=1)

    if not acquired:
        return

    try:
        _poll_worlds(worlds)
    finally:
        try:
            lock.release()
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("Could not release lock: %s", ex)


def _split_polls(worlds):
    max_worlds = settings.BOUNDLESS_MAX_WORLDS_PER_POLL
    worlds = list(worlds)

    num_runs = len(worlds) // max_worlds + 1
    logger.info("Spliting polling into %s runs", num_runs)
    run = 1
    while len(worlds) > max_worlds:
        worlds_ids = [w.id for w in worlds[:max_worlds]]
        logger.info("Run %s: %s", run, worlds_ids)
        poll_worlds_split.delay(worlds_ids)
        worlds = worlds[max_worlds:]
        run += 1

    if len(worlds) > 0:
        worlds_ids = [w.id for w in worlds]
        logger.info("Run %s: %s", run, worlds_ids)
        poll_worlds_split.delay(worlds_ids)


def _mark_world_inactive(world):
    logger.info("World %s no longer in API, marking inactive...", world)
    world.active = False
    world.save()

    if world.is_exo:
        resources = None
        wp = world.worldpoll_set.all().order_by("time").first()
        if wp is not None:
            resources = wp.resources
        ExoworldExpiredNotification.objects.send_notification(world, resources)


def _poll_world(client, world):
    world_dict = client.get_world_data(SimpleWorld(world.id, world.api_url))
    poll_data = None
    world_data = None
    if world_dict is not None:
        world_data = world_dict["worldData"]

        if not world_data.get("locked"):
            poll_token = world_dict["pollData"]
            poll_data = client.get_world_poll(
                SimpleWorld(world.id, world_data["apiURL"]),
                poll_token=poll_token,
            )

    return world_data, poll_data


def _handle_rd(*args, world=None, **kwargs):
    if world is None:
        return True

    logger.warning("RemoteDisconnected while polling world %s", world)
    return False


def _handle_http(*args, world=None, response=None, **kwargs):
    if world is None or response is None:
        return True

    if world.is_sovereign and response.status_code == 400:
        logger.warning("Could not do poll world %s", world)
        return False
    return True


def _handle_error(*args, world=None, exception=None, **kwargs):
    if world is None or exception is None:
        return True

    logger.error("%s while polling world %s", exception, world)
    return True


def _poll_worlds(worlds):
    total = len(worlds)
    if total > settings.BOUNDLESS_MAX_WORLDS_PER_POLL:
        _split_polls(worlds)
        return

    client = BoundlessClient()
    logger.info("Boundless user: %s", client.user["boundless"]["username"])

    error_handler = GameErrorHandler(
        rd_callback=_handle_rd,
        http_callback=_handle_error,
        error_callback=_handle_error,
    )
    poll_world = error_handler(_poll_world)
    for index, world in enumerate(worlds):
        WorldPoll.objects.filter(world=world, active=True).update(active=False)

        logger.info("Polling world %s (%s/%s)", world.display_name, index + 1, total)
        response = poll_world(client=client, world=world)

        if response.has_error:
            continue

        world_data, poll_data = response.response
        if world_data is None:
            _mark_world_inactive(world)
            continue

        try:
            world, _ = World.objects.get_or_create_from_game_dict(world_data)
        except Exception:
            logger.warning(world_data)
            raise

        if world.is_locked or (world.end is not None and timezone.now() > world.end):
            logger.info("World %s expired, not polling...", world)
            continue

        if poll_data is not None:
            try:
                WorldPoll.objects.create_from_game_dict(
                    world_data, poll_data, world=world
                )
            except Exception:
                logger.warning(poll_data)
                raise


@app.task
def calculate_distances(world_ids=None):
    if world_ids is None:
        worlds = World.objects.filter(active=True)
        all_worlds = worlds
    else:
        worlds = World.objects.filter(id__in=world_ids)
        all_worlds = World.objects.filter(active=True)

    client = BoundlessClient()

    world_ids = {w.id for w in all_worlds}

    for world in worlds:
        world_distances = WorldDistance.objects.filter(
            Q(world_source=world) | Q(world_dest=world)
        ).select_related("world_source", "world_dest")

        world_distance_ids = set()
        for world_distance in world_distances:
            if world_distance.world_source.id == world_distance.world_dest.id:
                world_distance_ids.add(world.id)
            else:
                if world_distance.world_source.id != world.id:
                    world_distance_ids.add(world_distance.world_source.id)
                if world_distance.world_dest.id != world.id:
                    world_distance_ids.add(world_distance.world_dest.id)

        missing_distance_ids = world_ids.difference(world_distance_ids)

        logger.info(
            "Missing %s distance calulcation(s) for %s",
            len(missing_distance_ids),
            world,
        )
        for world_id in missing_distance_ids:
            world_dest = World.objects.get(id=world_id)

            world.get_distance_to_world(world_dest, client=client)


@app.task
def poll_settlements(world_ids=None):
    if world_ids is None:
        worlds = (
            World.objects.filter(
                api_url__isnull=False,
                is_public=True,
                is_creative=False,
                is_locked=False,
            )
            .filter(Q(active=True) | Q(end__isnull=False, end__gt=timezone.now()))
            .order_by("id")
        )
    else:
        worlds = World.objects.filter(id__in=world_ids)

    client = BoundlessClient()
    colors = Color.objects.all()

    error_handler = GameErrorHandler(
        rd_callback=_handle_rd,
        http_callback=_handle_error,
        error_callback=_handle_error,
    )

    @error_handler
    def _poll_settlements(client, world):
        return client.get_world_settlements(SimpleWorld(world.id, world.api_url))

    for world in worlds:
        response = _poll_settlements(client=client, world=world)

        if response.has_error:  # pylint: disable=no-member
            continue

        settlements = response.response  # pylint: disable=no-member
        Settlement.objects.filter(world=world).delete()

        for settlement in settlements:
            Settlement.objects.create_from_game_obj(world, settlement, colors=colors)

        logger.info("Found %s settlements for %s", len(settlements), world)
