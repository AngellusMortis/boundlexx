import socket
from datetime import timedelta
from email.utils import parsedate_to_datetime

import requests
from azure.mgmt.cdn import CdnManagementClient
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from msrestazure.azure_active_directory import ServicePrincipalCredentials
from requests.exceptions import ReadTimeout

from boundlexx.api.utils import (
    PURGE_CACHE_LOCK,
    PURGE_CACHE_PATHS,
    PURGE_GROUPS,
    queue_purge_paths,
)
from config.celery_app import app

MAX_SINGLE_PURGE = 50
WARM_WORLD_DUMP_TASK = "boundlexx.api.tasks.warm_world_dump"

logger = get_task_logger(__name__)


def _path_chunks(iterable, chunk_size):
    while len(iterable) > chunk_size:
        yield iterable[:chunk_size]
        iterable = iterable[chunk_size:]
    yield iterable


@app.task
def purge_cache(all_paths=False):
    if all_paths:
        paths = PURGE_GROUPS["__all__"]
    else:
        with cache.lock(PURGE_CACHE_LOCK, expire=10, auto_renewal=False):
            paths = cache.get(PURGE_CACHE_PATHS)

            if paths is not None:
                cache.delete(PURGE_CACHE_PATHS)

        if paths is None or len(paths) == 0:
            logger.warning("No paths to purge")
            return

        paths = list(paths)

    if (
        settings.AZURE_CDN_ENDPOINT_NAME is None
        or len(settings.AZURE_CDN_ENDPOINT_NAME) == 0
    ):
        logger.warning("Azure settings not configured")
        return

    try:
        credentials = ServicePrincipalCredentials(
            settings.AZURE_CLIENT_ID,
            settings.AZURE_CLIENT_SECRET,
            tenant=settings.AZURE_TENANT_ID,
        )

        client = CdnManagementClient(credentials, settings.AZURE_SUBSCRIPTION_ID)

        for paths_group in _path_chunks(paths, MAX_SINGLE_PURGE):
            logger.info("Purging paths: %s", paths_group)

            poller = client.endpoints.purge_content(
                settings.AZURE_CDN_RESOURCE_GROUP,
                settings.AZURE_CDN_PROFILE_NAME,
                settings.AZURE_CDN_ENDPOINT_NAME,
                paths_group,
            )
            poller.result()
    except (Exception, socket.gaierror) as ex:  # pylint: disable=broad-except
        logger.info("Rescheduling paths: %s", paths)
        queue_purge_paths(paths)

        if "No address associated with hostname" not in str(ex):
            raise


def _reschedule(run_time):
    task = PeriodicTask.objects.filter(task=WARM_WORLD_DUMP_TASK).first()

    if task is None:
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=1, period=IntervalSchedule.SECONDS
        )

        task = PeriodicTask.objects.create(
            task=WARM_WORLD_DUMP_TASK,
            name="Warm Cache - World Dump",
            interval=interval,
            one_off=True,
            start_time=run_time,
            enabled=True,
        )
    else:
        task.one_off = True
        task.start_time = run_time
        task.enabled = True
        task.save()


@app.task
def warm_world_dump():
    lock = cache.lock("boundlexx:api:warm_world_dump")

    acquired = lock.acquire(blocking=True, timeout=1)

    if not acquired:
        return

    rescheduled = False
    try:
        domain = Site.objects.get_current().domain
        path = reverse("api:world-dump")

        try:
            r = requests.get(f"https://{domain}{path}", timeout=10)
        except (requests.HTTPError, ReadTimeout):
            logger.info("Timeout while making request, rescheduling...")
            _reschedule(timezone.now() + timedelta(seconds=60))
            rescheduled = True
            return

        if not r.ok:
            logger.info("Bad response code, rescheduling...")
            _reschedule(timezone.now() + timedelta(seconds=60))
            rescheduled = True
            return

        if "X-Cache" not in r.headers or r.headers["X-Cache"] != "HIT":
            logger.info("Response not cached, rescheduling...")
            _reschedule(timezone.now() + timedelta(seconds=10))
            rescheduled = True
            return

        expires = parsedate_to_datetime(r.headers["Expires"])

        if expires < timezone.now():
            logger.info("Expiration date in the past! Rescheduling...")
            _reschedule(timezone.now() + timedelta(minutes=5))
            rescheduled = True
            return

        logger.info("Request cached! Rescheduling for %s", expires)
        _reschedule(expires + timedelta(seconds=5))
        rescheduled = True
    finally:
        if not rescheduled:
            _reschedule(timezone.now() + timedelta(seconds=60))
        lock.release()
