from datetime import datetime

import gspread
import pytz
from celery.utils.log import get_task_logger
from django.conf import settings

from boundlexx.boundless.models import Color, Item, World, WorldBlockColor
from boundlexx.notifications.models import ExoworldNotification
from config.celery_app import app

logger = get_task_logger(__name__)


def _get_lifetimes(raw_lifetime):
    parts = raw_lifetime.strip().split(",")

    if len(parts) != 2:
        return None, None

    start = int(parts[0])
    end = int(parts[1])

    if end == 0:
        end_time = None
    else:
        end_time = datetime.utcfromtimestamp(end).replace(tzinfo=pytz.utc)

    return (
        datetime.utcfromtimestamp(start).replace(tzinfo=pytz.utc),
        end_time,
    )


def _update_world(world, start, end, row):
    if world.start is None and start is not None:
        world.start = start
    if world.end is None and end is not None:
        world.end = end
    if world.end is not None and world.start is not None and world.size is None:
        world.size = 192  # exo worlds are always 192
    if world.region is None:
        world.region = row[4].strip()
    if len(row[5].strip()) > 0 and world.assignment_id is None:
        world.assignment_id = int(row[5].strip())
    if world.tier is None:
        world.tier = int(row[7].strip()) - 1
    if world.world_type is None:
        world.world_type = row[8].strip().upper()

        if world.world_type == "UMBRIS":
            world.world_type = "DARKMATTER"

    world.save()

    return world


def _create_block_colors(world, block_colors, item_names):
    block_colors_created = 0
    for index, item_name in enumerate(item_names):
        raw_block_color = block_colors[index].strip().split(",")

        if len(raw_block_color) == 0 or raw_block_color[0].strip() == "":
            continue

        color_id = int(raw_block_color[0].strip())
        if color_id == 0:
            continue

        item = Item.objects.filter(string_id=f"ITEM_TYPE_{item_name}").first()

        if item is None:
            continue

        color = Color.objects.get(game_id=int(raw_block_color[0].strip()))
        block_color, created = WorldBlockColor.objects.get_or_create_color(
            world=world, item=item, color=color
        )

        if created:
            block_colors_created += 1

        block_color.save()

    if block_colors_created > 0:
        ExoworldNotification.objects.send_update_notification(world)

    logger.info("%s: created %s color(s)", world, block_colors_created)


@app.task
def ingest_world_data():
    gc = gspread.service_account()
    sheet = gc.open_by_url(settings.BOUNDLESS_SHEETS_WORLDS_URL).sheet1

    rows = list(sheet.get_all_values())
    header_columns = rows[0]
    rows = rows[1:]
    # do new worlds first
    rows.reverse()

    for row in rows:
        if len(row[0].strip()) == 0:
            continue

        world_id = int(row[0].strip())
        display_name = row[1].strip()
        start, end = _get_lifetimes(row[3])

        world = World.objects.filter(id=world_id).first()

        if world is None and end is not None:
            world = World.objects.get_and_replace_expired_exo(
                world_id, display_name, end
            )

        if world is None:
            world = World.objects.create(id=world_id, display_name=display_name)

        world = _update_world(world, start, end, row)
        _create_block_colors(world, row[11:-5], header_columns[11:-5])
