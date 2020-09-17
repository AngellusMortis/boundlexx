from __future__ import annotations

from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import intcomma, naturaltime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django_celery_results.models import TaskResult
from polymorphic.models import PolymorphicManager, PolymorphicModel

from boundlexx.api.utils import get_base_url
from boundlexx.notifications.tasks import send_discord_webhook

User = get_user_model()


class SubscriptionBase(PolymorphicModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)

    def send(self, **kwargs):
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

                data["content"] = f'{meantions_prefix.strip()}\n{data["content"]}'

        return data

    def send(
        self, embed=None, files=None, markdown=None
    ):  # pylint: disable=arguments-differ
        if embed is None and markdown is None:
            raise ValueError("embed or markdown required")

        data_list = []
        if embed is not None:
            data = {"embeds": embed, "content": ""}
            data = self._add_meantions_to_data(data, "roles", self.roles)
            data = self._add_meantions_to_data(data, "users", self.users)

            data_list.append(data)
        else:
            messages = markdown.split("%SPLIT_MESSAGE%")
            send_meantions = False
            data_list = []
            for m in messages:
                if len(m.strip()) == 0:
                    continue

                data = {"content": m}

                if not send_meantions:
                    data = self._add_meantions_to_data(data, "roles", self.roles)
                    data = self._add_meantions_to_data(data, "users", self.users)
                    send_meantions = True

                data_list.append(data)

        send_discord_webhook.delay(self.webhook_url, data_list, files)


class NotificationBase(PolymorphicModel):
    subscription = models.ForeignKey(SubscriptionBase, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def markdown(self, **kwargs):
        return None

    def embed(self, *args, **kwargs):
        return None, None

    def _markdown_replace(self, message):
        return (
            message.replace("\xa0", " ")
            .replace("&#x27;", "'")
            .replace("&quot;", "'")
            .replace("&quot;", "'")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )


class BaseNotificationManager(PolymorphicManager):
    def send_notification(self, message):
        notifications = self.filter(active=True)

        for notification in notifications:
            notification.subscription.send(message)


class PolymorphicNotificationManager(PolymorphicManager):
    def send_notification(self, *args):
        notifications = self.filter(active=True)

        for notification in notifications:
            embed, files = notification.embed(*args)
            markdown = notification.markdown(*args)

            notification.subscription.send(embed=embed, files=files, markdown=markdown)


class NewWorldNotificationManager(PolymorphicNotificationManager):
    def send_new_notification(self, world_poll):
        world = world_poll.world

        if world.is_exo:
            ExoworldNotification.objects.send_notification(world, world_poll.resources)
        elif world.is_creative:
            CreativeWorldNotification.objects.send_notification(
                world, world_poll.resources
            )
        elif world.is_sovereign:
            SovereignWorldNotification.objects.send_notification(
                world, world_poll.resources
            )
        else:
            return

        if (
            world.image.name
            and world.forum_id
            and world.worldblockcolor_set.count() > 0
        ):
            world.notification_sent = True
        else:
            world.notification_sent = False

            world.save()

    def send_update_notification(self, world):
        send_update = (
            world.address is not None
            and world.notification_sent is False
            and (
                (world.forum_id and world.image.name)
                or timezone.now() > world.start + timedelta(days=1)
                or not world.is_exo
            )
        )

        if send_update:
            if world.is_exo:
                ExoworldNotification.objects.send_notification(world)
            elif world.is_creative:
                CreativeWorldNotification.objects.send_notification(world)
            elif world.is_sovereign:
                SovereignWorldNotification.objects.send_notification(world)
            else:
                return

            world.notification_sent = True
            world.save()


class ExoworldNotification(NotificationBase):
    objects = NewWorldNotificationManager()

    _context = None
    _world_type = "exoworld"

    def _get_context(self, world, resources=None):
        if self._context is not None:
            return self._context

        # never get colors for Creative worlds
        if world.is_creative:
            colors = None
        else:
            colors = world.worldblockcolor_set.all().order_by("item__game_id")
            if colors.count() == 0:
                colors = None

        color_groups: Dict[str, list] = {}
        if colors is not None:
            for group_name in settings.BOUNDLESS_WORLD_POLL_GROUP_ORDER:
                color_groups[group_name] = []

            for color in colors:
                item_id = color.item.game_id
                group_name = settings.BOUNDLESS_WORLD_POLL_COLOR_GROUPINGS[item_id]

                order_index = list(
                    settings.BOUNDLESS_WORLD_POLL_GROUP_ORDER[group_name]
                ).index(item_id)
                color_group: List[Tuple[int, str]] = color_groups[group_name]
                color_group.append((order_index, color))
                color_groups[group_name] = color_group

            for group_name in list(color_groups.keys()):
                if len(color_groups[group_name]) == 0:
                    del color_groups[group_name]
                    continue

                color_groups[group_name] = [
                    c[1] for c in sorted(color_groups[group_name], key=lambda g: g[0])
                ]

        context = {"world": world, "color_groups": color_groups}
        if resources is not None:
            embedded_resources = []
            surface_resources = []

            for resource in resources.order_by("-count"):
                if resource.is_embedded:
                    embedded_resources.append(resource)
                else:
                    surface_resources.append(resource)

            context["embedded_resources"] = embedded_resources
            context["surface_resources"] = surface_resources

        self._context = context
        return self._context

    def markdown(self, world, resources=None):  # pylint: disable=arguments-differ
        context = self._get_context(world, resources)

        message = ""
        if resources is None:
            message = render_to_string(
                "boundlexx/notifications/exoworld_update.md",
                context,
            )
        else:
            message = render_to_string(
                "boundlexx/notifications/exoworld.md",
                context,
            )

        return self._markdown_replace(message)

    def _main_embed(self, world, is_update=False):
        files: Optional[Dict[str, str]] = None

        main_embed = {}
        main_embed["title"] = world.display_name

        if is_update:
            main_embed[
                "description"
            ] = f"New information is avaiable for the new {self._world_type}!"
        else:
            main_embed["description"] = f"A new {self._world_type} world as appeared!"

        if world.forum_url:
            main_embed["url"] = world.forum_url

        if world.image.name:
            main_embed["thumbnail"] = {"url": f"attachment://{world.image.name}"}

            files = {world.image.name: world.image.url}

        main_embed["fields"] = [
            {
                "name": "ID",
                "value": f"{world.name} ({world.id})",
                "inline": True,
            },
            {
                "name": "Server",
                "value": f"{world.address}",
                "inline": True,
            },
            {
                "name": "Start",
                "value": (f"{naturaltime(world.start)}\n" f"{world.start.isoformat()}"),
                "inline": True,
            },
            {
                "name": "End",
                "value": f"{naturaltime(world.end)}\n{world.end.isoformat()}",
                "inline": True,
            },
            {
                "name": "Server Region",
                "value": f"{world.get_region_display()}",
                "inline": True,
            },
            {
                "name": "Tier",
                "value": f"{world.get_tier_display()}",
                "inline": True,
            },
            {
                "name": "World Type",
                "value": f"{world.get_world_type_display()}",
                "inline": True,
            },
            {
                "name": "Protection",
                "value": f"{world.protection}",
                "inline": True,
            },
            {
                "name": "World Size (16-block chunks)",
                "value": f"{world.size}",
                "inline": True,
            },
            {
                "name": "Number of Regions",
                "value": f"{world.number_of_regions}",
                "inline": True,
            },
            {
                "name": "Surface Liquid",
                "value": f"{world.surface_liquid}",
                "inline": True,
            },
            {
                "name": "Core Liquid",
                "value": f"{world.core_liquid}",
                "inline": True,
            },
        ]

        if world.assignment is not None:
            value = f"{world.assignment}"
            if world.assignment_distance is not None:
                value += (
                    f" @{world.assignment_distance} blinksecs"
                    f" ({world.assignment_cost}c)"
                )

            main_embed["fields"].append(
                {
                    "name": "Closest Planet",
                    "value": value,
                }
            )

        return main_embed, files

    def _resource_embed(self, embedded_resources, surface_resources):
        resource_embed: dict = {"title": "World Resources"}
        fields: List[Dict[str, str]] = []

        resource_groups = (
            (embedded_resources, "Embedded Resources"),
            (surface_resources, "Surface Resources"),
        )
        for resources, title in resource_groups:
            values = [""]
            for index, resource in enumerate(resources):
                rank = index + 1
                value = values[-1]

                new_value = (
                    f"\n#{rank} **{resource.item.english}**: "
                    f"_{resource.percentage}% ({intcomma(resource.count)})_"
                )

                value += new_value
                if len(value) > 1024:
                    values.append(new_value)
                else:
                    values[-1] = value

            if len(values[0]) > 0:
                for index, value in enumerate(values):
                    if index > 0:
                        title += " (cont.)"
                    fields.append(
                        {
                            "name": title,
                            "value": value,
                        }
                    )

        if len(fields) == 0:
            return None

        resource_embed["fields"] = fields
        return resource_embed

    def _color_embed(self, color_groups):
        color_embed: dict = {"title": "Block Colors"}
        fields: List[Dict[str, str]] = []
        for group_name, color_group in color_groups.items():
            value = ""
            for color in color_group:
                value += (
                    f"\n* **{color.item.english}**: "
                    f"_{color.color.default_name} ({color.color.game_id})_"
                )

                extra = []
                if color.is_new_color:
                    extra.append("**NEW**")
                if color.exist_via_transform:
                    extra.append("**TRANSFORM**")
                if color.exist_via_transform:
                    extra.append(f"**Days: {color.days_since_last}**")

                value += f" {' | '.join(extra)}"

            fields.append(
                {"name": group_name.title() or "Gleam", "value": value.strip()}
            )

        if len(fields) == 0:
            return None

        color_embed["fields"] = fields
        return color_embed

    def embed(self, world, resources=None):  # pylint: disable=arguments-differ
        context = self._get_context(world, resources)

        embeds = []
        main_embed, files = self._main_embed(world, resources is None)
        embeds.append(main_embed)

        if resources is not None:
            resource_embed = self._resource_embed(
                context["embedded_resources"], context["surface_resources"]
            )
            if resource_embed is not None:
                embeds.append(resource_embed)

        color_embed = self._color_embed(context["color_groups"])
        if color_embed is not None:
            embeds.append(color_embed)

        return embeds, files


class SovereignWorldNotification(ExoworldNotification):
    _world_type = "sovereign world"


class CreativeWorldNotification(ExoworldNotification):
    _world_type = "creative world"


class FailedTaskNotification(NotificationBase):
    objects = PolymorphicNotificationManager()

    def markdown(self, task):  # pylint: disable=arguments-differ
        output = task.traceback.split("\n")

        messages = []
        message: List[str] = []
        for line in output:
            if len("\n".join(message) + line) >= 1750:
                messages.append(message)
                message = []
            message.append(line)
        messages.append(message)

        return self._markdown_replace(
            render_to_string(
                "boundlexx/notifications/failed_task.md",
                {
                    "task": task,
                    "messages": messages,
                    "base_url": get_base_url(admin=True),
                },
            )
        )


@receiver(post_save, sender=TaskResult)
def task_failure_handler(sender, instance, **kwargs):
    if (
        instance.status == "FAILURE"
        and instance.task_name != "boundlexx.notifications.tasks.send_discord_webhook"
    ):
        FailedTaskNotification.objects.send_notification(instance)
