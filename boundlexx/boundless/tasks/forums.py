import re
import time
from datetime import timedelta, timezone
from distutils.util import strtobool
from typing import List, Optional, Union

import dateparser
import requests
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils import timezone as dj_timezone
from filetype.filetype import get_type

from boundlexx.boundless.models import Color, LocalizedName, World, WorldBlockColor
from boundlexx.boundless.utils import clean_image
from config.celery_app import app

logger = get_task_logger(__name__)

FORUM_PARSE_TOPIC_CACHE_KEY = "boundless:parsed_topics"

FORUM_EXO_WORLD_CATEGORY = "exoworlds/31"
FORUM_PERM_WORLD_CATEGORY = "worlds/33"
FORUM_SOVEREIGN_WORLD_CATEGORY = "sovereign/39"
DEFAULT_IMAGE = "https://forum.playboundless.com/uploads/default/original/3X/6/8/683d21dfac3159456b0074eb6fa1898be6ec9e97.png"  # noqa: E501
PERM_REGEX = re.compile(r".*alt=\"(Yes|No)\".* (Visit|Edit|Claim)")
ALLOWED_KEYS = (
    "name",
    "id",
    "type",
    "tier",
    "start",
    "end",
    "server",
    "visit",
    "edit",
    "claim",
)


def _get_topics(category: str):
    topics_to_parse = []
    parse_cache = cache.get(FORUM_PARSE_TOPIC_CACHE_KEY, [])

    next_url: Optional[str] = f"/c/creations/{category}.json"
    while next_url is not None:
        response = requests.get(f"{settings.BOUNDLESS_FORUM_BASE_URL}{next_url}")
        response.raise_for_status()

        topic_list = response.json()["topic_list"]
        if "more_topics_url" in topic_list:
            next_url = topic_list["more_topics_url"].replace(
                category, f"{category}.json"
            )
        else:
            next_url = None

        topics = topic_list["topics"]

        for topic in topics:
            if (
                topic["id"] in settings.BOUNDLESS_FORUM_BAD_TOPICS
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

    # Waxy Foliage/Weeping Waxcap and Twisted Wood Trunk/Twisted Aloba
    # have similar names, make sure we know the difference
    if "Wax" in parts[0] and parts[0] != "Weeping Waxcap":
        parts[0] = "Waxy Foliage"
    elif "Twisted" in parts[0] and parts[0] != "Twisted Aloba":
        parts[0] = "Twisted Wood Trunk"

    return parts


def _get_item_and_color(colors, parts):
    item = None
    try:
        item = LocalizedName.objects.get(lang="english", name=parts[0]).game_obj
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
        parts = parts[0].split(" –", 1)

    if len(parts) == 1:
        parts = parts[0].split(" - ", 1)

    # name
    name = parts[0].replace("[", "").replace("]", "")
    tier = None
    world_type = None
    end = None

    # tier + world_type
    type_str = parts[1].lower()
    match = re.search(r"(t|tier )(\d)", type_str)
    if match:
        tier = match.group(2)

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


def _get_world_image(raw_html, name):
    image = None

    if "lightbox" in str(raw_html)[:100]:
        images = raw_html.find_all("a", {"class": "lightbox"})
        attribute = "href"
    else:
        images = raw_html.find_all("img")
        attribute = "src"

    if len(images) > 0:
        if attribute == "src":
            if images[0].get("width") != "300" or images[0].get("height") != "300":
                return None

        image_url = images[0].get(attribute)
        if image_url == DEFAULT_IMAGE:
            return None
        logger.info("Downloading image for topic %s", image_url)

        response = requests.get(image_url)
        response.raise_for_status()

        extension = "jpg"
        file_type = get_type(response.headers.get("content-type", None))
        if file_type is not None:
            extension = file_type.extension

        image = ContentFile(clean_image(response.content))
        image.name = f"{name}.{extension}".lower().replace(" ", "_")

    return image


def _parse_permissions(perm_string):
    perms = perm_string.split(" : ")[1].split(" | ")

    global_perms: List[List[Union[str, bool]]] = []

    for perm in perms:
        match = PERM_REGEX.match(perm)

        if match:
            global_perms.append(
                [match.group(2).lower(), bool(strtobool(match.group(1).lower()))]
            )

    return global_perms


def _parse_line(line, raw_line):
    parsed_line = None

    if " : " in line:
        parts = [
            p.encode("utf8").decode("ascii", errors="ignore").strip()
            for p in line.split(" : ")
        ]

        if parts[0] == "world":
            parts[0] = "name"
        elif parts[0] == "region":
            parts[0] = "server"
        elif parts[0] == "appeared":
            parts[0] = "start"
        elif parts[0] == "last until" or parts[0] == "last seen":
            parts[0] = "end"

        if len(parts[0]) == 0 or parts[0] in ("∞", ">= 0"):
            return None

        if parts[0] == "name":
            parts[1] = raw_line.split(" : ")[-1].strip()

        parsed_line = parts
    elif "appeared" in line:
        parsed_line = ["start", line.split("appeared ")[-1].strip()]
    elif "last until" in line:
        parsed_line = ["end", line.split("last until ")[-1].strip()]
    elif "last seen" in line:
        parsed_line = ["end", line.split("last seen ")[-1].strip()]

    return parsed_line


def _parse_world_info(raw_html):
    raw_html_lines = str(raw_html).split("\n")
    lines = raw_html.get_text().split("\n")

    parsed_lines = []
    for index, raw_line in enumerate(lines):
        line = raw_line.strip().lower()

        if "permissions" in line:
            perms = _parse_permissions(raw_html_lines[index])
            parsed_lines += perms
            continue

        # nothing else to parse
        if "blocks color" in line:
            break

        parsed_line = _parse_line(line, raw_line)
        if parsed_line is not None:
            parsed_lines.append(parsed_line)

    parsed_data = {}
    for line in parsed_lines:
        if line[0] in ALLOWED_KEYS:
            parsed_data[line[0]] = line[1]

    return parsed_data


def _normalize_world_info(world_info):  # pylint: disable=too-many-branches
    if "type" in world_info:
        world_info["type"] = world_info["type"].upper()

    if "server" in world_info:
        for region_choice in World.Region.choices:
            choices = [region_choice[0].lower(), region_choice[1].lower()]
            if world_info["server"] in choices:
                world_info["server"] = region_choice[0]
                break

    if "start" in world_info:
        start = dateparser.parse(world_info["start"])
        if start is None:
            del world_info["start"]
        else:
            world_info["start"] = start.replace(tzinfo=timezone.utc)

    if "end" in world_info:
        end = dateparser.parse(world_info["end"])
        if end is None:
            del world_info["end"]
        else:
            world_info["end"] = end.replace(tzinfo=timezone.utc)

    if "tier" in world_info:
        # NAME (#)
        match = re.match(r"\w+ \((\d+)\)", world_info["tier"])
        if match:
            world_info["tier"] = match.group(1)

        # T# - NAME
        match = re.match(r"t(\d+) - \w+", world_info["tier"])
        if match:
            world_info["tier"] = match.group(1)
        world_info["tier"] = int(world_info["tier"]) - 1

    if "id" in world_info:
        try:
            world_info["id"] = int(world_info["id"])
        except ValueError:
            del world_info["id"]

    return world_info


def _parse_forum_topic(topic: int, is_perm: bool, is_sovereign: bool = False):
    logger.info("Paring topic: %s", topic)
    response = requests.get(f"{settings.BOUNDLESS_FORUM_BASE_URL}/t/{topic}.json")
    response.raise_for_status()

    data = response.json()

    world_info = {}
    # players often set the title to whatever. do not parse
    if not is_sovereign:
        world_info = _parse_title(data["title"])
    raw_html = BeautifulSoup(data["post_stream"]["posts"][0]["cooked"], "html.parser")

    # players not using our template
    if is_sovereign and "-------------------" not in str(raw_html):
        logger.warning("Sovereign post not using standard format: %s", topic)
        return None, None

    title_name = world_info.get("name")
    world_info.update(_parse_world_info(raw_html))
    world_info = _normalize_world_info(world_info)

    if is_sovereign and "name" not in world_info:
        logger.warning("Sovereign post malformed: %s", topic)
        return None, None

    if title_name is not None and world_info["name"] != title_name:
        logger.warning(
            "Different between world name in title and forum post: %s vs. %s",
            title_name,
            world_info["name"],
        )
        world_info["name"] = title_name

    image = _get_world_image(raw_html, world_info["name"])
    if image is not None:
        world_info["image"] = image

    # perm has no end
    if is_perm:
        expected_fields = 7
        if "end" in world_info:
            del world_info["end"]
    else:
        expected_fields = 8

    # Sovereign has perms
    if is_sovereign:
        expected_fields += 3

    if len(world_info) < expected_fields:
        logger.warning(
            "Could not parse all world data for topic %s\nFound %s\n%s",
            topic,
            list(world_info.keys()),
            raw_html.get_text().split("\n"),
        )

    details = raw_html.find_all("details")

    block_details = None
    for detail in details:
        if "Blocks Color" in detail.summary.get_text().strip():
            block_details = detail
            break

    return world_info, block_details


def _ingest_world_data(topics, is_perm=False, is_sovereign=False):
    logger.info("Found %s topic(s) to parse", len(topics))
    for topic in topics:
        world_info, block_details = _parse_forum_topic(
            topic, is_perm=is_perm, is_sovereign=is_sovereign
        )

        if world_info is None:
            continue

        block_colors = []
        if block_details is not None:
            block_colors = _parse_block_details(block_details)
        world, _ = World.objects.get_or_create_forum_world(
            topic, world_info, is_sovereign
        )

        if world is None:
            logger.info("Could find world for topic: %s", topic)
            continue

        number_created = 0
        for block_color in block_colors:
            _, created = WorldBlockColor.objects.get_or_create_color(
                world=world, item=block_color[0], color=block_color[1]
            )

            if created:
                number_created += 1

        if world.id < settings.BOUNDLESS_EXO_EXPIRED_BASE_ID:
            # only add world as parsed if the data is "complete" and has image
            cutoff = dj_timezone.now() - timedelta(days=7)
            if "image" in world_info or world.start < cutoff:
                parse_cache = cache.get(FORUM_PARSE_TOPIC_CACHE_KEY, [])
                parse_cache.append(topic)
                cache.set(FORUM_PARSE_TOPIC_CACHE_KEY, parse_cache, timeout=2592000)

            logger.info(
                "Topic %s: Imported %s block color details for world %s",
                topic,
                number_created,
                world,
            )


@app.task
def ingest_sovereign_world_data(topics=None):
    lock = cache.lock(
        "boundlexx:tasks:ingest:sovereign", expire=120, auto_renewal=False
    )

    acquired = lock.acquire(blocking=True, timeout=1)

    if not acquired:
        return

    try:
        if topics is None:
            topics = _get_topics(FORUM_SOVEREIGN_WORLD_CATEGORY)

        _ingest_world_data(topics, True, True)
    finally:
        try:
            lock.release()
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("Could not release lock: %s", ex)


@app.task
def ingest_exo_world_data(topics=None):
    lock = cache.lock("boundlexx:tasks:ingest:exo", expire=120, auto_renewal=False)

    acquired = lock.acquire(blocking=True, timeout=1)

    if not acquired:
        return

    try:
        if topics is None:
            topics = _get_topics(FORUM_EXO_WORLD_CATEGORY)

        _ingest_world_data(topics, False, False)
    finally:
        try:
            lock.release()
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("Could not release lock: %s", ex)


@app.task
def ingest_perm_world_data(topics=None):
    lock = cache.lock("boundlexx:tasks:ingest:perm", expire=120, auto_renewal=False)

    acquired = lock.acquire(blocking=True, timeout=1)

    if not acquired:
        return

    try:
        if topics is None:
            topics = _get_topics(FORUM_PERM_WORLD_CATEGORY)

        _ingest_world_data(topics, True, False)
    finally:
        try:
            lock.release()
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("Could not release lock: %s", ex)
