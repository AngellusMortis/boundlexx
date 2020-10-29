import djclick as click
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.db.models import Q

from boundlexx.boundless.models import World, WorldBlockColor
from boundlexx.boundless.tasks.forums import (
    ingest_exo_world_data,
    ingest_perm_world_data,
    ingest_sovereign_world_data,
)
from boundlexx.boundless.tasks.sheets import ingest_world_data
from boundlexx.boundless.tasks.shop import update_prices, update_prices_split, clean_up_queued_worlds
from boundlexx.boundless.tasks.worlds import (
    calculate_distances,
    discover_all_worlds,
    poll_creative_worlds,
    poll_exo_worlds,
    poll_perm_worlds,
    poll_sovereign_worlds,
    poll_worlds,
    search_new_worlds,
)
from config.celery_app import app

logger = get_task_logger(__name__)
User = get_user_model()

__all__ = [
    "add_world_control_data",
    "calculate_distances",
    "clean_up_queued_worlds",
    "discover_all_worlds",
    "ingest_exo_world_data",
    "ingest_perm_world_data",
    "ingest_sovereign_world_data",
    "ingest_world_data",
    "poll_creative_worlds",
    "poll_exo_worlds",
    "poll_perm_worlds",
    "poll_sovereign_worlds",
    "poll_worlds",
    "recalculate_colors",
    "search_new_worlds",
    "search_new_worlds",
    "update_prices_split",
    "update_prices",
]

NON_EXO = Q(world__end__isnull=True) | Q(world__owner__isnull=False)
EXO = {
    "world__isnull": False,
    "world__end__isnull": False,
    "world__owner__isnull": True,
}


def _get_block_colors(world_ids):
    if world_ids is not None:
        wbcs = WorldBlockColor.objects.filter(world_id__in=world_ids)
    else:
        wbcs = WorldBlockColor.objects.all()

    return wbcs.order_by("world_id")


@app.task
def recalculate_colors(world_ids=None, log=None):
    if log is None:
        log = logger.info

    wbcs = _get_block_colors(world_ids)
    log("Updating timing for all world block colors...")
    with click.progressbar(
        wbcs.iterator(), length=wbcs.count(), show_percent=True, show_pos=True
    ) as pbar:
        for block_color in pbar:
            if block_color.world is not None and block_color.world.start:
                block_color.time = block_color.world.start
                block_color.save()

    wbcs = _get_block_colors(world_ids)
    log("Recalculcating dynamic properties...")
    with click.progressbar(
        wbcs.iterator(), length=wbcs.count(), show_percent=True, show_pos=True
    ) as pbar:
        for block_color in pbar:
            block_color.is_new = False
            block_color.first_world = None
            block_color.last_exo = None
            block_color.is_new_transform = False
            block_color.transform_first_world = None
            block_color.transform_last_exo = None

            if block_color.world is not None and block_color.world.is_creative:
                block_color.save()
                continue

            base_compare = WorldBlockColor.objects.filter(
                item=block_color.item,
                color=block_color.color,
                is_default=True,
                time__lt=block_color.time,
            ).filter(Q(world__isnull=True) | Q(world__is_creative=False))

            wbc = base_compare.filter(NON_EXO).order_by("world__start").first()
            block_color.is_new = wbc is None
            if wbc is not None:
                block_color.first_world = wbc.world

            wbc = base_compare.filter(**EXO).order_by("-world__start").first()
            if wbc is not None:
                block_color.last_exo = wbc.world

            if block_color.transform_group is None:
                block_color.save()
                continue

            base_transform = WorldBlockColor.objects.filter(
                item_id__in=block_color.transform_group,
                color=block_color.color,
                is_default=True,
                time__lt=block_color.time,
            ).filter(Q(world__isnull=True) | Q(world__is_creative=False))

            if block_color.is_new:
                wbc = base_transform.filter(NON_EXO).first()
                block_color.is_new_transform = wbc is None
                if wbc is not None and wbc.world is not None:
                    block_color.transform_first_world = wbc.world

                wbc = base_compare.filter(**EXO).first()
                if wbc is not None:
                    block_color.transform_last_exo = wbc.world
            else:
                block_color.is_new_transform = False

            block_color.save()


@app.task
def add_world_control_data(world_id, world_control_data, user_id):
    user = User.objects.get(id=user_id)

    ws_data = {}
    for block_id, data in world_control_data.items():
        ws_data[int(block_id)] = data

    block_colors_created = WorldBlockColor.objects.create_colors_from_wc(
        World.objects.get(pk=world_id), ws_data, logger=logger, user=user
    )

    logger.info("Created %s color(s)", block_colors_created)

    if block_colors_created > 0:
        recalculate_colors.delay([world_id])
