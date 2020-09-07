import socket

from azure.mgmt.cdn import CdnManagementClient
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache
from msrestazure.azure_active_directory import ServicePrincipalCredentials

from boundlexx.api.utils import (
    PURGE_CACHE_LOCK,
    PURGE_CACHE_PATHS,
    PURGE_GROUPS,
    queue_purge_paths,
)
from config.celery_app import app

MAX_SINGLE_PURGE = 50

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

    credentials = ServicePrincipalCredentials(
        settings.AZURE_CLIENT_ID,
        settings.AZURE_CLIENT_SECRET,
        tenant=settings.AZURE_TENANT_ID,
    )

    client = CdnManagementClient(credentials, settings.AZURE_SUBSCRIPTION_ID)

    for paths_group in _path_chunks(paths, MAX_SINGLE_PURGE):
        logger.info("Purging paths: %s", paths_group)

        try:
            poller = client.endpoints.purge_content(
                settings.AZURE_CDN_RESOURCE_GROUP,
                settings.AZURE_CDN_PROFILE_NAME,
                settings.AZURE_CDN_ENDPOINT_NAME,
                paths_group,
            )
            poller.result()
        except socket.gaierror:
            logger.info("Rescheduling paths: %s", paths)
            queue_purge_paths(paths)
        except Exception:
            logger.info("Rescheduling paths: %s", paths)
            queue_purge_paths(paths)
            raise
