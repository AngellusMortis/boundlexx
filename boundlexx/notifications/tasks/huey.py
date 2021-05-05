import json
import logging
import time
from io import BytesIO
from typing import IO, Optional

import httpx

from boundlexx.utils import get_forum_client
from config.huey_app import huey

__all__ = ["send_discord_webhook"]

logger = logging.getLogger("huey")


DISCORD_LOCK_KEY = "discord_webhook:lock"
DISCORD_CALL_KEY = "discord_webhook:call"
# Discord Webhook rate limit is 30 request/min
DISCORD_DELAY = 2
FORUM_LOCK_KEY = "forum_post:lock"
FORUM_CALL_KEY = "forum_post:call"
FORUM_DELAY = 2


def _sleep(last_call, delay):
    now = time.monotonic()
    time_since = now - last_call
    if time_since < delay:
        sleep_time = delay - time_since
        logger.info("Sleeping %s", sleep_time)
        time.sleep(sleep_time)


@huey.task()
def error_task():
    raise Exception("test")


@huey.task(retries=5, retry_delay=5, priority=100)
@huey.lock_task(DISCORD_LOCK_KEY)
def send_discord_webhook(
    webhook_url: str, data_list: list[dict], files: Optional[dict[str, str]] = None
):
    last_call = huey.cache.get(DISCORD_CALL_KEY) or 0

    message_count = len(data_list)
    logger.info("%s Discord messages to send", message_count)
    for index, data in enumerate(data_list):
        if message_count > 1:
            logger.info("Send %s of %s Discord messages", index + 1, message_count)
        _sleep(last_call, DISCORD_DELAY)

        logger.debug(
            "URL: %s, data: %s, files: %s",
            webhook_url,
            json.dumps(data),
            json.dumps(files),
        )

        if files is None:
            response = httpx.post(
                webhook_url,
                content=json.dumps(data),
                headers={"Content-Type": "application/json"},
            )
        else:
            raw_files: dict[str, IO[bytes]] = {}
            for filename, file_url in files.items():
                logger.info("Downloading file URL %s", file_url)
                file_response = httpx.get(file_url)
                file_response.raise_for_status()

                raw_files[filename] = BytesIO(file_response.content)

            response = httpx.post(
                webhook_url,
                data={"payload_json": json.dumps(data)},
                files=raw_files,
            )

        if response.is_error:
            logger.warning(response.text)
        response.raise_for_status()
        logger.debug(response.headers)
        logger.debug(response.text)

        last_call = time.monotonic()
        huey.cache.set(DISCORD_CALL_KEY, last_call, DISCORD_DELAY)


@huey.task(retries=5, retry_delay=5, priority=90)
@huey.lock_task(FORUM_LOCK_KEY)
def update_forum_post(topic_id, title, content, wiki=False):
    last_call = huey.cache.get(FORUM_CALL_KEY) or 0
    client = get_forum_client()

    _sleep(last_call, FORUM_DELAY)

    logger.info("Updating title of topic...")
    client.update_topic(f"/t/-/{topic_id}.json", title=title)
    last_call = time.monotonic()
    _sleep(last_call, FORUM_DELAY)

    logger.info("Getting initial post ID...")
    response = client.topic_posts(topic_id)
    last_call = time.monotonic()

    first_post = response["post_stream"]["posts"][0]

    _sleep(last_call, FORUM_DELAY)

    logger.info("Updating initial post body...")
    client.update_post(first_post["id"], content)
    last_call = time.monotonic()

    if wiki and not first_post["wiki"]:
        _sleep(last_call, FORUM_DELAY)

        logger.info("Ensuring initial post is a wiki...")
        client._put(  # pylint: disable=protected-access
            f"/posts/{first_post['id']}/wiki", wiki="true"
        )
        last_call = time.monotonic()
    huey.cache.set(FORUM_CALL_KEY, last_call, FORUM_DELAY)


@huey.task(retries=5, retry_delay=5, priority=90)
@huey.lock_task(FORUM_LOCK_KEY)
def create_forum_post(world_id=None, wiki=False, **kwargs):
    last_call = huey.cache.get(FORUM_CALL_KEY) or 0

    _sleep(last_call, FORUM_DELAY)

    client = get_forum_client()
    logger.info("Creating post...")
    response = client.create_post(**kwargs)
    last_call = time.monotonic()

    _sleep(last_call, FORUM_DELAY)

    if wiki:
        logger.info("Ensuring initial post is a wiki...")
        client._put(  # pylint: disable=protected-access
            f"/posts/{response['id']}/wiki", wiki="true"
        )
        last_call = time.monotonic()
        huey.cache.set(FORUM_CALL_KEY, last_call, FORUM_DELAY)

    if world_id is not None:
        logger.info(
            "Updating world %s with topic ID: %s", world_id, response["topic_id"]
        )

        response = huey.api_client.post(
            "/ingest/world-forum-id/",
            content=json.dumps(
                {"world_id": world_id, "forum_id": int(response["topic_id"])}
            ),
        )

        if response.is_error:
            logger.error(
                "Failed to update world with topic ID: %s %s",
                response.status_code,
                response.content,
            )
