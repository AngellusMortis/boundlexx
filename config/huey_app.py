import logging
from typing import Optional

import environ
import httpx
from huey import PriorityRedisHuey
from redis import ConnectionPool, Redis

__all__ = ["huey"]

env = environ.Env()
logger = logging.getLogger("huey")
pool = ConnectionPool(
    host=env("REDIS_HOST"),
    port=env.int("REDIS_PORT"),
    max_connections=env.int("HUEY_MAX_CONNECTIONS"),
)


class Huey(PriorityRedisHuey):
    _cache: Optional[Redis] = None
    _api_client: Optional[httpx.Client] = None
    has_django: bool = False

    @property
    def error_webhook(self) -> Optional[str]:
        return env("HUEY_ERROR_WEBHOOK", default=None)

    @property
    def api_client(self):
        if self._api_client is None:
            self._api_client = httpx.Client(
                timeout=5, base_url=env("HUEY_BOUNDLEXX_API_URL_BASE")
            )
            self._api_client.headers.update(
                {
                    "Authorization": f"Token {env('HUEY_BOUNDLEXX_API_TOKEN')}",
                    "Content-Type": "application/json",
                }
            )

        return self._api_client

    @property
    def cache(self) -> Redis:
        if self._cache is None:
            if self.has_django:
                from django.core.cache import cache

                self._cache = cache
            else:
                self._cache = Redis(connection_pool=pool)

        return self._cache

    def _check_for_django(self):
        try:
            from django.core.exceptions import AppRegistryNotReady

            try:
                from boundlexx.boundless.models import World  # noqa
            except AppRegistryNotReady:
                pass
            else:
                self.has_django = True
        except ImportError:
            pass

    def create_consumer(self, **options):
        self._check_for_django()

        logger.info("Connection pool: %s", self.storage.pool)
        if self.has_django:
            logger.info("Initialized WITH Django support")
        else:
            logger.info("Initialized WITHOUT Django support")

        return super().create_consumer(**options)


huey = Huey("boundlexx", connection_pool=pool)
