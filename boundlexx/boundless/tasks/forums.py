import re
import time
from datetime import timezone
from typing import Optional

import dateparser
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
            if (
                topic["id"] in settings.BOUNDLESS_FORUM_EXO_BAD_TOPICS
                or topic["id"] in parse_cache
            ):
                continue

            topics_to_parse.append(topic["id"])

        time.sleep(1)

    return topics_to_parse


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
            block_color = _get_item_and_color(colors, parts)
            if block_color is not None:
                block_colors.append(block_color)

    return block_colors


def _parse_title(title):
    parts = title.split("--")
    parts = [p.strip() for p in parts]

    if len(parts) == 1:
        parts = parts[0].split(" - ", 1)

        if len(parts) == 1:
            parts = parts[0].split(" –", 1)

    # name
    name = parts[0].replace("[", "").replace("]", "")
    tier = None
    world_type = None
    end = None

    # tier + world_type
    type_str = parts[1].lower()
    match = re.search(r"(t|tier )(\d)", type_str)
    if match:
        tier = int(match.group(2)) - 1

    for choice in World.WorldType.choices:
        if choice[0].lower() in type_str:
            world_type = choice[0]
            break

    # end
    if len(parts) > 2:
        end_str = parts[2].lower()
        if "]" in end_str:
            end_str = end_str.split("]")[0].strip()

        if "last seen" in end_str:
            end = end_str.split("last seen")[-1].strip()

    world_info = {"name": name}

    if tier is not None:
        world_info["tier"] = tier
    if world_type is not None:
        world_info["type"] = world_type
    if end is not None:
        world_info["end"] = end

    return world_info


def _parse_world_info(raw_html):
    lines = raw_html.get_text().split("\n")

    parsed_lines = []
    for raw_line in lines:
        line = raw_line.strip().lower()

        # nothing else to parse
        if "blocks color" in line:
            break

        if " : " in line:
            parts = [
                p.encode("utf8").decode("ascii", errors="ignore").strip()
                for p in line.split(" : ")
            ]

            if parts[0] == "world":
                parts[0] = "name"

            if len(parts[0]) == 0 or parts[0] in ("∞", ">= 0"):
                continue

            if parts[0] == "name":
                parts[1] = raw_line.split(" : ")[-1].strip()

            parsed_lines.append(parts)
        elif "appeared" in line:
            parsed_lines.append(["start", line.split("appeared ")[-1].strip()])
        elif "last until" in line:
            parsed_lines.append(["end", line.split("last until ")[-1].strip()])
        elif "last seen" in line:
            parsed_lines.append(["end", line.split("last seen ")[-1].strip()])

    parsed_data = {}
    for line in parsed_lines:
        if line[0] in ("name", "type", "tier", "start", "end", "server"):
            parsed_data[line[0]] = line[1]

    return parsed_data


def _normalize_world_info(world_info):
    if "type" in world_info:
        world_info["type"] = world_info["type"].upper()

    if "server" in world_info:
        for region_choice in World.Region.choices:
            choices = [region_choice[0].lower(), region_choice[1].lower()]
            if world_info["server"] in choices:
                world_info["server"] = region_choice[0]
                break

    if "start" in world_info:
        world_info["start"] = dateparser.parse(world_info["start"]).replace(
            tzinfo=timezone.utc
        )

    if "end" in world_info:
        world_info["end"] = dateparser.parse(world_info["end"]).replace(
            tzinfo=timezone.utc
        )

    return world_info


def _parse_forum_topic(topic):
    response = requests.get(
        f"{settings.BOUNDLESS_FORUM_BASE_URL}/t/{topic}.json"
    )
    response.raise_for_status()

    data = response.json()

    world_info = _parse_title(data["title"])
    raw_html = BeautifulSoup(
        data["post_stream"]["posts"][0]["cooked"], "html.parser"
    )

    world_info.update(_parse_world_info(raw_html))
    world_info = _normalize_world_info(world_info)

    if len(world_info) < 6:
        logger.warning(
            "Could not parse all world data for topic %s\nFound %s\n%s",
            topic,
            world_info.keys(),
            raw_html.get_text().split("\n"),
        )

    details = raw_html.find_all("details")

    block_details = None
    for detail in details:
        if "Blocks Color" in detail.summary.get_text().strip():
            block_details = detail
            break

    return world_info, block_details


@app.task
def ingest_exo_world_data():
    topics = _get_topics()

    logger.info("Found %s topic(s) to parse", len(topics))
    for topic in topics:
        world_info, block_details, = _parse_forum_topic(topic)

        block_colors = _parse_block_details(block_details)
        world, _ = World.objects.get_or_create_unknown_world(world_info)

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
