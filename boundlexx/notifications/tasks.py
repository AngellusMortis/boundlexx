import json
import time

import requests
from celery.utils.log import get_task_logger
from django.core.cache import cache

from boundlexx.notifications.utils import get_forum_client
from config.celery_app import app

logger = get_task_logger(__name__)


# Discord Webhook rate limit is 30 request/min
DISCORD_DELAY = 2

FORUM_DELAY = 2


def _sleep(last_call, delay):
    now = time.monotonic()
    time_since = now - last_call
    if time_since < delay:
        time.sleep(delay - time_since)


@app.task
def send_discord_webhook(webhook_url, data_list, files=None):
    with cache.lock("discord_webhook:lock", expire=10 * len(data_list)):
        cache_key = "discord_webhook:call"
        last_call = cache.get(cache_key) or 0

        for data in data_list:
            _sleep(last_call, DISCORD_DELAY)

            logger.debug(
                "URL: %s, data: %s, files: %s",
                webhook_url,
                json.dumps(data),
                json.dumps(files),
            )

            if files is None:
                response = requests.post(
                    webhook_url,
                    data=json.dumps(data),
                    headers={"Content-Type": "application/json"},
                )
            else:
                for filename, file_url in files.items():
                    logger.info("Downloading file URL %s", file_url)
                    file_response = requests.get(file_url)
                    file_response.raise_for_status()

                    files[filename] = file_response.content

                response = requests.post(
                    webhook_url,
                    data={"payload_json": json.dumps(data)},
                    files=files,
                )

            if not response.ok:
                logger.warning(response.text)
            response.raise_for_status()
            logger.debug(response.headers)
            logger.debug(response.text)

            last_call = time.monotonic()
            cache.set(cache_key, last_call, timeout=DISCORD_DELAY)


@app.task
def create_forum_post(world_id=None, **kwargs):
    from boundlexx.boundless.models import World  # pylint: disable=cyclic-import

    with cache.lock("forum_post:lock", expire=20):
        cache_key = "forum_post:call"
        last_call = cache.get(cache_key) or 0

        _sleep(last_call, FORUM_DELAY)

        client = get_forum_client()
        logger.info("Creating post...")
        response = client.create_post(**kwargs)
        last_call = time.monotonic()

        _sleep(last_call, FORUM_DELAY)

        logger.info("Ensuring initial post is a wiki...")
        client._put(  # pylint: disable=protected-access
            f"/posts/{response['id']}/wiki", wiki="true"
        )
        last_call = time.monotonic()
        cache.set(cache_key, last_call, timeout=FORUM_DELAY)

        if world_id is not None:
            logger.info(
                "Updating world %s with topic ID: %s", world_id, response["topic_id"]
            )
            World.objects.filter(id=world_id).update(forum_id=response["topic_id"])


@app.task
def update_forum_post(topic_id, title, content):
    with cache.lock("forum_post:lock", expire=40):
        cache_key = "forum_post:call"
        last_call = cache.get(cache_key) or 0
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

        if not first_post["wiki"]:
            _sleep(last_call, FORUM_DELAY)

            logger.info("Ensuring initial post is a wiki...")
            client._put(  # pylint: disable=protected-access
                f"/posts/{first_post['id']}/wiki", wiki="true"
            )
            last_call = time.monotonic()
        cache.set(cache_key, last_call, timeout=FORUM_DELAY)
