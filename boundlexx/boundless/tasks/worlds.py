from typing import List

from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from requests.exceptions import HTTPError

from boundlexx.boundless.client import HTTP_ERRORS, BoundlessClient
from boundlexx.boundless.models import World, WorldDistance, WorldPoll
from config.celery_app import app

logger = get_task_logger(__name__)


@app.task
def search_new_worlds():
    existing_worlds = World.objects.filter(
        id__lt=settings.BOUNDLESS_EXO_EXPIRED_BASE_ID,
        end__isnull=False,
        end__gt=timezone.now() - settings.BOUNDLEXX_WORLD_SEARCH_OFFSET,
    ).order_by("id")

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
        return

    all_ids = set(
        range(lowest_id, highest_id + 1 + settings.BOUNDLESS_EXO_SEARCH_RADIUS)
    )

    ids_to_scan = sorted(all_ids - existing_ids)

    logger.info("Starting scan for exo worlds (%s)", ids_to_scan)

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
                    world_data, poll_dict = client.get_world_poll(
                        world_dict["pollData"], world_dict["worldData"]
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

    worlds: List[dict] = []

    for world_id in ids_to_scan:
        world_data = client.get_world_data(world_id)

        if world_data is not None:
            worlds.append(world_data)

    return worlds


@app.task
def poll_perm_worlds():
    _poll_worlds(World.objects.filter(end__isnull=True, active=True))


@app.task
def poll_exo_worlds():
    _poll_worlds(
        World.objects.filter(owner__isnull=True, end__isnull=False, active=True)
    )


@app.task
def poll_sovereign_worlds():
    _poll_worlds(
        World.objects.filter(owner__isnull=False, is_creative=False, active=True)
    )


@app.task
def poll_creative_worlds():
    _poll_worlds(
        World.objects.filter(owner__isnull=False, is_creative=True, active=True)
    )


@app.task
def poll_worlds(world_ids=None):
    if world_ids is None:
        worlds = World.objects.filter(active=True)
    else:
        worlds = World.objects.filter(id__in=world_ids)

    _poll_worlds(worlds)


def _poll_worlds(worlds):
    client = BoundlessClient()
    errors_total = 0

    for world in worlds:
        WorldPoll.objects.filter(world=world, active=True).update(active=False)

        logger.info("Polling world %s", world.display_name)

        try:
            world_data, poll_data = client.get_world_poll_by_id(world.id)
        except HTTP_ERRORS as ex:
            if (
                world.is_sovereign
                and hasattr(ex, "response")
                and ex.response is not None  # type: ignore
                and ex.response.status_code == 400  # type: ignore
            ):
                logger.warning("Could not do poll world %s", world.display_name)
            else:
                errors_total += 1
                logger.error("%s while polling world %s", ex, world)

                if errors_total > 5:
                    raise Exception(  # pylint: disable=raise-missing-from
                        "Aborting due to large number of HTTP errors"
                    )
                continue

        if world_data is None:
            logger.info("World %s no longer in API, marking inactive...", world)
            world.active = False
            world.save()
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
