from __future__ import annotations

from typing import List

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_celery_results.models import TaskResult
from polymorphic.models import PolymorphicManager, PolymorphicModel

from boundlexx.api.utils import get_base_url
from boundlexx.celery.utils import get_output_for_task
from boundlexx.notifications.tasks import send_discord_webhook

User = get_user_model()


class SubscriptionBase(PolymorphicModel):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=32, blank=True, null=True)

    def send(self, message):
        raise NotImplementedError()


class DiscordWebhookSubscription(SubscriptionBase):
    webhook_url = models.CharField(max_length=256)
    roles = models.TextField(blank=True, null=True)
    users = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.owner is None:
            return f"{self.id}: {self.name}"
        return f"{self.id} ({self.owner}): {self.name}"

    def _add_meantions_to_data(self, data, key, value):
        if value is not None:
            meantions = []
            for m in value.split(","):
                if len(m.strip()) > 0:
                    meantions.append(m.strip())

            if len(meantions) > 0:
                meantions_prefix = ""
                for meantion in meantions:
                    if key == "roles":
                        meantions_prefix = f"<@&{meantion}> {meantions_prefix}"
                    else:
                        meantions_prefix = f"<@{meantion}> {meantions_prefix}"

                data[
                    "content"
                ] = f'{meantions_prefix.strip()}\n{data["content"]}'

        return data

    def send(self, message):
        messages = message.split("%SPLIT_MESSAGE%")

        send_meantions = False
        for m in messages:
            if len(m.strip()) == 0:
                continue

            data = {"content": m}

            if not send_meantions:
                data = self._add_meantions_to_data(data, "roles", self.roles)
                data = self._add_meantions_to_data(data, "users", self.users)
                send_meantions = True

            send_discord_webhook.delay(self.webhook_url, data)


class NotificationBase(PolymorphicModel):
    subscription = models.ForeignKey(
        SubscriptionBase, on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)

    def markdown(self, **kwargs):
        raise NotImplementedError()


class BaseNotificationManager(PolymorphicManager):
    def send_notification(self, message):
        notifications = self.filter(active=True)

        for notification in notifications:
            notification.subscription.send(message)


class MarkdownNotificationManager(PolymorphicManager):
    def send_notification(self, *args):
        notifications = self.filter(active=True)

        for notification in notifications:
            message = notification.markdown(*args)

            notification.subscription.send(message)


class ExoworldNotificationManager(MarkdownNotificationManager):
    def send_new_notification(self, world_poll):
        super().send_notification(world_poll.world, world_poll.resources)

    def send_update_notification(self, world):
        super().send_notification(world)


class ExoworldNotification(NotificationBase):
    objects = ExoworldNotificationManager()

    def markdown(
        self, world, resources=None
    ):  # pylint: disable=arguments-differ

        colors = world.worldblockcolor_set.all().order_by("item__game_id")
        if colors.count() == 0:
            colors = None

        if colors is not None:
            colors = list(colors)
            if len(colors) > 30:
                colors = [colors[:30], colors[30:]]
            else:
                colors = [colors]

        if resources is not None:
            resources = resources.order_by("item__game_id")

        message = ""
        if resources is None:
            message = render_to_string(
                "boundlexx/notifications/exoworld_update.md",
                {"world": world, "colors": colors},
            )
        else:
            message = render_to_string(
                "boundlexx/notifications/exoworld.md",
                {"world": world, "resources": resources, "colors": colors},
            )

        return (
            message.replace("\xa0", " ")
            .replace("&#x27;", "'")
            .replace("&quot;", "'")
        )


class FailedTaskNotification(NotificationBase):
    objects = MarkdownNotificationManager()

    def markdown(self, task):  # pylint: disable=arguments-differ
        output = get_output_for_task(task)
        output += task.traceback.split("\n")

        messages = []
        message: List[str] = []
        for line in output:
            if len("\n".join(message) + line) >= 1750:
                messages.append(message)
                message = []
            message.append(line)
        messages.append(message)

        return (
            render_to_string(
                "boundlexx/notifications/failed_task.md",
                {
                    "task": task,
                    "messages": messages,
                    "base_url": get_base_url(),
                },
            )
            .replace("\xa0", " ")
            .replace("&#x27;", "'")
            .replace("&quot;", "'")
        )


@receiver(post_save, sender=TaskResult)
def task_failure_handler(sender, instance, **kwargs):
    if (
        instance.status == "FAILURE"
        and instance.task_name
        != "boundlexx.notifications.tasks.send_discord_webhook"
    ):
        FailedTaskNotification.objects.send_notification(instance)
