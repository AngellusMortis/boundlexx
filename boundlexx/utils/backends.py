from django_prometheus.cache.backends.redis import (
    RedisCache as RedisPrometheusCache,
)
from redis_lock.django_cache import RedisCache as RedisLockCache


class RedisCache(RedisLockCache, RedisPrometheusCache):
    pass
