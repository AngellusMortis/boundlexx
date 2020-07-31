import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache

from boundlexx.boundless.models import (
    Color,
    LocalizedName,
    World,
    WorldBlockColor,
)
from config.celery_app import app

logger = get_task_logger(__name__)

FORUM_PARSE_TOPIC_CACHE_KEY = "boundless:parsed_exo_topics"


def _get_topics():
    topics_to_parse = []
    archive_topic = None
    parse_cache = cache.get(FORUM_PARSE_TOPIC_CACHE_KEY, [])

    next_url: Optional[str] = "/c/creations/exoworlds/31.json"
    while next_url is not None:
        response = requests.get(
            f"{settings.BOUNDLESS_FORUM_BASE_URL}{next_url}"
        )
        response.raise_for_status()

        topic_list = response.json()["topic_list"]
        if "more_topics_url" in topic_list:
            next_url = topic_list["more_topics_url"].replace("31", "31.json")
        else:
            next_url = None

        topics = topic_list["topics"]

        for topic in topics:
            if "The Exoworlds Archives" in topic["title"]:
                archive_topic = topic["id"]
            elif (
                topic["id"] in settings.BOUNDLESS_FORUM_EXO_BAD_TOPICS
                or topic["id"] in parse_cache
            ):
                continue
            else:
                topics_to_parse.append(topic["id"])

        time.sleep(1)

    return archive_topic, topics_to_parse


def _parse_forum_topic(topic):
    response = requests.get(
        f"{settings.BOUNDLESS_FORUM_BASE_URL}/t/{topic}.json"
    )
    response.raise_for_status()

    data = response.json()

    title = data["title"]
    title = (
        title.split("--")[0]
        .strip()
        .replace("[", "")
        .replace("]", "")
        .split(" –")[0]
        .split(" - ")[0]
        .split(" :")[0]
    )

    soup = BeautifulSoup(
        data["post_stream"]["posts"][0]["cooked"], "html.parser"
    )

    details = soup.find_all("details")

    block_details = None
    for detail in details:
        if "Blocks Color" in detail.summary.get_text().strip():
            block_details = detail
            break

    return title, block_details


def _get_or_create_world(title):
    try:
        world = World.objects.get(display_name=title)
    except World.DoesNotExist:
        highest_world = (
            World.objects.filter(
                id__gte=settings.BOUNDLESS_EXO_EXPIRED_BASE_ID
            )
            .order_by("-id")
            .first()
        )

        if highest_world is None:
            highest_id = settings.BOUNDLESS_EXO_EXPIRED_BASE_ID - 1
        else:
            highest_id = highest_world.id

        world = World.objects.create(
            active=False, id=highest_id + 1, display_name=title
        )

    return world


def _clean_line(line):
    parts = []
    for part in line.split(" - "):
        cleaned = part.encode("utf8").decode("ascii", errors="ignore").strip()

        if len(cleaned) > 0:
            parts.append(cleaned)

    if len(parts) == 3:
        try:
            int(parts[2].replace("<", ""))
        except ValueError:
            pass
        else:
            parts = [parts[0], parts[1]]

    for name, corrected_name in settings.BOUNDLESS_FORUM_NAME_MAPPINGS.items():
        if name in parts[0]:
            parts[0] = corrected_name

    # Waxy Foilage/Weeping Waxcap and Twisted Wood Trunk/Twisted Aloba
    # have similar names, make sure we know the difference
    if "Wax" in parts[0] and parts[0] != "Weeping Waxcap":
        parts[0] = "Waxy Foliage"
    elif "Twisted" in parts[0] and parts[0] != "Twisted Aloba":
        parts[0] = "Twisted Wood Trunk"

    return parts


def _get_item_and_color(colors, parts):
    item = None
    try:
        item = LocalizedName.objects.get(
            lang="english", name=parts[0]
        ).game_obj
    except LocalizedName.DoesNotExist:
        pass

    match = re.search(r"\d+", parts[1])
    color = None
    if match:
        color = colors[int(match.group())]
    else:
        for color_obj in colors.values():
            if color_obj.default_name == parts[1]:
                color = color_obj
                break

    if color is None or item is None:
        logger.warning("Could not parse %s", parts)
    else:
        return item, color
    return None


def _parse_block_details(block_details):
    lines = block_details.get_text().strip().split("\n")

    colors = {}
    color_names = []
    for color in Color.objects.all().prefetch_related("localizedname_set"):
        color_names.append(color.default_name)
        colors[color.game_id] = color

    block_colors = []
    for line in lines:
        parts = []
        if re.search(r"\d", line) and ">=" not in line:
            parts = _clean_line(line)
        else:
            for color in color_names:
                if color in line:
                    parts = _clean_line(line)

        if len(parts) == 2:
            item, color = _get_item_and_color(colors, parts)
            if item is None and color is not None:
                block_colors.append([item, color])

    return block_colors


@app.task
def ingest_exo_world_data():
    _, topics = _get_topics()

    logger.info("Found %s topic(s) to parse", len(topics))
    for topic in topics:
        display_name, block_details = _parse_forum_topic(topic)

        world = _get_or_create_world(display_name)
        block_colors = _parse_block_details(block_details)

        number_created = 0

        for block_color in block_colors:
            _, created = WorldBlockColor.objects.get_or_create(
                world=world,
                item=block_color[0],
                defaults={"color": block_color[1]},
            )

            if created:
                number_created += 1

        parse_cache = cache.get(FORUM_PARSE_TOPIC_CACHE_KEY, [])
        parse_cache.append(topic)
        cache.set(FORUM_PARSE_TOPIC_CACHE_KEY, parse_cache)

        logger.info(
            "Topic %s: Imported %s block color details for world %s",
            topic,
            number_created,
            world,
        )
