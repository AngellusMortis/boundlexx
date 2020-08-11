import json
import time

import requests
from celery.utils.log import get_task_logger
from django.core.cache import cache

from config.celery_app import app

logger = get_task_logger(__name__)


@app.task
def send_discord_webhook(webhook_url, data_list):
    with cache.lock("discord_webhook:lock", expire=10 * len(data_list)):
        cache_key = "discord_webhook:call"
        last_call = cache.get(cache_key) or 0

        for data in data_list:
            now = time.monotonic()

            time_since = now - last_call
            if time_since < 1:
                time.sleep(1 - time_since)

            response = requests.post(
                webhook_url,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            last_call = time.monotonic()
            cache.set(cache_key, last_call, timeout=1)
