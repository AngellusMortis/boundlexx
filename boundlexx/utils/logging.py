import logging

from django.core.cache import cache

LOG_TIMEOUT = 43200  # 12 hours


class RedisTaskLogger(logging.Handler):
    def emit(self, record: logging.LogRecord):
        if not hasattr(record, "task_name"):
            return

        if not record.task_name.startswith("boundlexx"):  # type: ignore
            return

        with cache.lock(f"logger_lock.{record.task_id}"):  # type: ignore
            cache_key = f"logger.{record.task_id}"  # type: ignore

            output = cache.get(cache_key)
            if output is None:
                output = []

            output.append(
                f"[{record.asctime}: {record.levelname}] {record.message}"
            )

            cache.set(cache_key, output, timeout=LOG_TIMEOUT)
