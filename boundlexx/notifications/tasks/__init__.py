import traceback

from huey.api import Task
from huey.signals import SIGNAL_ERROR

from boundlexx.notifications.tasks.huey import (
    create_forum_post,
    error_task,
    send_discord_webhook,
    update_forum_post,
)
from config.huey_app import huey

try:
    from django.core.exceptions import AppRegistryNotReady
except ImportError:
    pass
else:
    try:
        from boundlexx.notifications.tasks.celery import error_task_celery
        from boundlexx.notifications.tasks.huey_django import set_notification_sent
    except AppRegistryNotReady:
        error_task_celery = None
        set_notification_sent = None


__all__ = [
    "create_forum_post",
    "error_task",
    "error_task_celery",
    "render_discord_messages",
    "send_discord_webhook",
    "set_notification_sent",
    "update_forum_post",
]

FAILED_TASK_TEMPLATE = """A task failed!

Task Name: `{name}` ({type})
Task ID: `{id}`
Output:
```
{output}
```
"""


def huey_template(task: Task, lines: list[str]):
    return FAILED_TASK_TEMPLATE.format(
        name=task.name, id=task.id, output="".join(lines), type="Huey"
    )


def celery_template(task, lines: list[str]):
    return FAILED_TASK_TEMPLATE.format(
        name=task.task_name, id=task.task_id, output="".join(lines), type="Celery"
    )


def render_discord_messages(is_huey: bool, **kwargs) -> list[dict]:
    task = kwargs.pop("task")

    if is_huey:
        exc = kwargs.pop("exc")
        lines = traceback.format_exception(exc, exc, exc.__traceback__)
    else:
        lines = [line + "\n" for line in task.traceback.split("\n")]

    messages_lines: list[list[str]] = []
    current_lines: list[str] = []

    for line in lines:
        if len("".join(current_lines) + line) >= 1750:
            messages_lines.append(current_lines)
            current_lines = []
        current_lines.append(line)
    messages_lines.append(current_lines)

    messages: list[dict] = []
    for index, lines in enumerate(messages_lines):
        if index == 0:
            messages.append(
                {
                    "content": huey_template(task, lines)
                    if is_huey
                    else celery_template(task, lines)
                }
            )
        else:
            messages.append({"content": f"```{''.join(lines)}```\n"})

    return messages


@huey.signal(SIGNAL_ERROR)
def on_task_error(signal, task: Task, exc):
    if task.name == "send_discord_webhook" or task.retries > 0:
        return

    if huey.has_django:
        from boundlexx.notifications.models import (  # noqa  # pylint: disable=cyclic-import
            FailedTaskNotification,
        )

        FailedTaskNotification.objects.send_notification(task, exc)
    elif huey.error_webhook is not None:
        messages = render_discord_messages(True, task=task, exc=exc)
        send_discord_webhook(huey.error_webhook, messages)
