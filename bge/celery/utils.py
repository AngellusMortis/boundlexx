from typing import List

from celery.app.task import Task
from django.core.cache import cache

from .models import TaskOutput


def get_output_for_task(task: Task) -> List[str]:
    output = []

    try:
        task_output = TaskOutput.objects.get(task=task)
    except TaskOutput.DoesNotExist:
        output = cache.get(f"logger.{task.task_id}", [])
    else:
        output = task_output.output.split("\n")

    return output
