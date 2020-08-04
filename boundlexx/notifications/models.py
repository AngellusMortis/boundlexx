from __future__ import annotations

import json
import time

import requests
from django.contrib.auth import get_user_model
from django.db import models
from django.template.loader import render_to_string
from polymorphic.models import PolymorphicManager, PolymorphicModel

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

            response = requests.post(
                self.webhook_url,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            time.sleep(1)


class NotificationBase(PolymorphicModel):
    subscription = models.ForeignKey(
        SubscriptionBase, on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)

    def markdown(self, **kwargs):
        raise NotImplementedError()


class ExoworldNotificationManager(PolymorphicManager):
    def send_new_notification(self, world_poll):
        notifications = self.filter(active=True)

        for notification in notifications:
            notification.subscription.send(
                notification.markdown(world_poll.world, world_poll.resources)
            )

    def send_update_notification(self, world):
        notifications = self.filter(active=True)

        for notification in notifications:
            notification.subscription.send(notification.markdown(world))


class ExoworldNotification(NotificationBase):
    objects = ExoworldNotificationManager()

    def markdown(
        self, world, resources=None
    ):  # pylint: disable=arguments-differ

        colors = world.worldblockcolor_set.all()
        if colors.count() == 0:
            colors = None

        if colors is not None:
            colors = sorted(colors, key=lambda s: s.item.english.lower())
            if len(colors) > 30:
                colors = [colors[:30], colors[30:]]
            else:
                colors = [colors]

        if resources is not None:
            resources = sorted(resources, key=lambda s: s.item.english.lower())

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

        return message.replace("\xa0", " ").replace("&#x27;", "'")
