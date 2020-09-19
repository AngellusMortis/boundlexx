import logging
import os

from celery import Celery
from celery.app.task import Task
from celery.signals import after_setup_task_logger, task_postrun
from django.core.cache import cache
from kombu import Queue

from boundlexx.utils.logging import RedisTaskLogger

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("boundlexx")
app.conf.task_default_queue = "default"
app.conf.task_queues = (
    Queue("default"),
    Queue("distance"),
    Queue("cache"),
    Queue("notify"),
    Queue("poll"),
    Queue("shop"),
)
app.conf.task_routes = {
    "boundlexx.boundless.tasks.worlds.calculate_distances": "distance",
    "boundlexx.api.tasks.purge_cache": "cache",
    "boundlexx.notifications.*": "notify",
    "boundlexx.boundless.tasks.worlds.poll_*": "poll",
    "boundlexx.boundless.tasks.shop.*": "shop",
}

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# pylint: disable=unused-argument
@after_setup_task_logger.connect
def setup_loggers(logger: logging.Logger, *args, **kwargs):
    redis_handler = RedisTaskLogger()

    logger.addHandler(redis_handler)


# pylint: disable=unused-argument
@task_postrun.connect
def after_task(task_id: str, task: Task, *args, **kwargs):
    # Django not loaded until here
    # pylint: disable=import-outside-toplevel
    from django_celery_results.models import TaskResult

    from boundlexx.celery.models import TaskOutput

    if not task.name.startswith("boundlexx"):
        return

    output = []
    with cache.lock(f"logger_lock.{task_id}"):
        cache_key = f"logger.{task_id}"

        output = cache.get(cache_key, [])
        cache.delete(cache_key)

    try:
        task_result = TaskResult.objects.get(task_id=task_id)
    except TaskResult.DoesNotExist:
        pass

    TaskOutput.objects.create(task=task_result, output="\n".join(output))
