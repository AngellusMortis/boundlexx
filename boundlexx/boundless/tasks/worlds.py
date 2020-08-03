from typing import List

from celery.utils.log import get_task_logger
from django.conf import settings

from boundlexx.boundless.client import BoundlessClient
from boundlexx.boundless.models import World, WorldPoll
from config.celery_app import app

logger = get_task_logger(__name__)


@app.task
def update_perm_worlds():
    client = BoundlessClient()

    worlds = client.gameservers.values()
    logger.info("Found %s worlds from discovery server.", len(worlds))

    worlds_created = 0
    for world_dict in worlds:
        _, created = World.objects.get_or_create_from_game_dict(world_dict)

        if created:
            worlds_created += 1

    logger.info("Import %s world(s)", worlds_created)


@app.task
def search_exo_worlds():
    most_recent_world = (
        World.objects.filter(id__lt=settings.BOUNDLESS_EXO_EXPIRED_BASE_ID)
        .order_by("-id")
        .first()
    )

    if most_recent_world is None:
        logger.warning("No worlds found to use as a start")
        return

    worlds_lower = max(
        most_recent_world.id - settings.BOUNDLESS_EXO_SEARCH_RADIUS, 1
    )
    worlds_upper = most_recent_world.id + settings.BOUNDLESS_EXO_SEARCH_RADIUS

    if worlds_lower == most_recent_world:
        worlds_lower += 1

    logger.info(
        "Starting scan for exo worlds (%s, %s)", worlds_lower, worlds_upper
    )

    _, worlds = _scan_worlds(worlds_lower, worlds_upper)

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
    for chunk in chunks:
        logger.info("Starting scan for worlds (%s, %s)", chunk[0], chunk[1])

        created, _ = _scan_worlds(chunk[0], chunk[1])
        worlds_found += created

    logger.info("Scan Complete. Found %s world(s)", worlds_found)


def _scan_worlds(lower, upper):
    client = BoundlessClient()
    worlds = get_worlds(lower, upper, client=client)

    worlds_found = 0
    world_objs = []
    for world_dict in worlds:
        world, created = World.objects.get_or_create_from_game_dict(
            world_dict["worldData"]
        )

        if created:
            worlds_found += 1
            world_objs.append(world)

            world_data, poll_dict = client.get_world_poll(
                world_dict["pollData"], world_dict["worldData"]
            )

            WorldPoll.objects.create_from_game_dict(
                world_data, poll_dict, world=world, new_world=True
            )

    logger.info("Found %s world(s)", worlds_found)

    return worlds_found, world_objs


def get_worlds(lower, upper, client=None):
    if client is None:
        client = BoundlessClient()

    worlds: List[dict] = []

    for world_id in range(lower, upper + 1):
        world_data = client.get_world_data(world_id)

        if world_data is not None:
            worlds.append(world_data)

    return worlds


@app.task
def poll_worlds(worlds=None):
    if worlds is None:
        worlds = World.objects.filter(active=True)

    client = BoundlessClient()

    for world in worlds:
        WorldPoll.objects.filter(world=world, active=True).update(active=False)

        logger.info("Polling world %s", world.display_name)
        world_data, poll_data = client.get_world_poll_by_id(world.id)

        if world_data is None:
            world.active = False
            world.save()
            continue

        World.objects.get_or_create_from_game_dict(world_data)

        if poll_data is not None:
            WorldPoll.objects.create_from_game_dict(
                world_data, poll_data, world=world
            )
