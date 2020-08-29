import json
import time

import requests
from celery.utils.log import get_task_logger
from django.core.cache import cache

from config.celery_app import app

logger = get_task_logger(__name__)


# Discord Webhook rate limit is 30 request/min
DISCORD_DELAY = 2


@app.task
def send_discord_webhook(webhook_url, data_list, files=None):
    with cache.lock("discord_webhook:lock", expire=10 * len(data_list)):
        cache_key = "discord_webhook:call"
        last_call = cache.get(cache_key) or 0

        for data in data_list:
            now = time.monotonic()

            time_since = now - last_call
            if time_since < DISCORD_DELAY:
                time.sleep(DISCORD_DELAY - time_since)

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
            cache.set(cache_key, last_call, timeout=1)
