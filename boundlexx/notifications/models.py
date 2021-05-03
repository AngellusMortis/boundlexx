from __future__ import annotations

import logging
import os
from datetime import timedelta
from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import intcomma, naturaltime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_results.models import TaskResult
from django_prometheus.models import ExportModelOperationsMixin
from PIL import Image
from polymorphic.models import PolymorphicManager, PolymorphicModel

from boundlexx.notifications.tasks import (
    create_forum_post,
    render_discord_messages,
    send_discord_webhook,
    set_notification_sent,
    update_forum_post,
)
from boundlexx.utils import download_image, get_forum_client

User = get_user_model()
logger = logging.getLogger(__file__)


class ForumImage(ExportModelOperationsMixin("forum_image"), models.Model):  # type: ignore # noqa E501
    class ImageType(models.IntegerChoices):
        COLOR = 0, _("Color")
        WORLD = 1, _("World")
        TYPE = 2, _("World Type")
        ATMOSPHERE = 3, _("Atmosphere")
        MISC = 4, _("Misc.")
        ITEM = 5, _("Item")

    image_type = models.PositiveSmallIntegerField(
        choices=ImageType.choices, db_index=True
    )
    lookup_id = models.CharField(db_index=True, max_length=64)
    url = models.TextField(db_index=True)
    shortcut_url = models.CharField(max_length=64)

    class Meta:
        unique_together = (
            "image_type",
            "lookup_id",
        )


class SubscriptionBase(PolymorphicModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        if self.owner is None:
            return f"{self.id}: {self.name}"
        return f"{self.id} ({self.owner}): {self.name}"

    def send(self, **kwargs):
        raise NotImplementedError()


class ForumCategorySubscription(ExportModelOperationsMixin("forum_category_subcription"), SubscriptionBase):  # type: ignore # noqa E501
    category_id = models.IntegerField(null=True, blank=True)

    def send(self, forum, **kwargs):  # pylint: disable=arguments-differ
        world, title, raw = forum

        if world.forum_id is None:
            create_forum_post(
                world_id=world.id,
                content=raw,
                category_id=self.category_id,
                title=title,
                wiki=True,
            )
        else:
            update_forum_post(world.forum_id, title, raw, wiki=True)


class ForumPMSubscription(ExportModelOperationsMixin("forum_pm_subcription"), SubscriptionBase):  # type: ignore # noqa E501
    pm_recipents = models.TextField(null=True, blank=True)

    def send(self, forum, **kwargs):  # pylint: disable=arguments-differ
        world, title, raw = forum

        create_forum_post(
            content=raw,
            title=title,
            archetype="private_message",
            target_recipients=self.pm_recipents,
            wiki=True,
        )


class DiscordWebhookSubscription(ExportModelOperationsMixin("discord_webhook_subcription"), SubscriptionBase):  # type: ignore # noqa E501
    webhook_url = models.CharField(max_length=256)
    roles = models.TextField(blank=True, null=True)
    users = models.TextField(blank=True, null=True)

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

    def send(  # pylint: disable=arguments-differ
        self,
        embed=None,
        files=None,
        markdown=None,
        **kwargs,
    ):
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

        send_discord_webhook(self.webhook_url, data_list, files)


class NotificationBase(PolymorphicModel):
    subscription = models.ForeignKey(SubscriptionBase, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def markdown(self, *args, **kwargs):
        return None

    def embed(self, *args, **kwargs):
        return None, None

    def forum(self, *args, **kwargs):
        return None, None, None

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
            forum = notification.forum(*args)

            notification.subscription.send(
                embed=embed, files=files, markdown=markdown, forum=forum
            )


class NewWorldNotificationManager(PolymorphicNotificationManager):
    def set_notification_sent(self, world_id, sent):
        set_notification_sent(world_id, sent)

    def send_new_notification(self, world_poll):
        world = world_poll.world

        if world.is_exo:
            if world.active:
                ExoworldNotification.objects.send_notification(
                    world, world_poll.resources
                )
        elif world.is_creative:
            CreativeWorldNotification.objects.send_notification(
                world, world_poll.resources
            )
        elif world.is_sovereign:
            SovereignWorldNotification.objects.send_notification(
                world, world_poll.resources
            )
        else:
            HomeworldNotification.objects.send_notification(world, world_poll.resources)

        if world.is_sovereign or (
            world.image.name
            and world.forum_id
            and world.worldblockcolor_set.count() > 0
        ):
            self.set_notification_sent(world.id, True)
        else:
            self.set_notification_sent(world.id, False)

    def send_update_notification(self, world):
        send_update = (
            world.address is not None
            and world.notification_sent is False
            and (
                (world.forum_id and world.image.name)
                or not world.is_exo
                or timezone.now() > world.start + timedelta(days=1)
            )
        )

        logger.info(
            "Update notification for %s. notification sent status: %s",
            world,
            world.notification_sent,
        )

        if world.is_sovereign:
            send_update = False
            self.set_notification_sent(world.id, True)

        if send_update:
            # no sovereign/creative worlds
            # Block Colors change over time
            if world.is_exo:
                if world.active:
                    ExoworldNotification.objects.send_notification(world)
            elif world.is_perm:
                HomeworldNotification.objects.send_notification(world)

            self.set_notification_sent(world.id, True)


class WorldNotification(NotificationBase):
    objects = NewWorldNotificationManager()

    _context = None
    _world_type = "world"

    def _get_colors(self, world, default=False):
        # never get colors for Creative worlds
        if world.is_creative:
            colors = None
        else:
            kwargs = {"active": True}
            if default:
                kwargs = {"is_default": True}

            colors = (
                world.worldblockcolor_set.filter(**kwargs)
                .select_related(
                    "item",
                    "color",
                    "first_world",
                    "last_exo",
                    "transform_first_world",
                    "transform_last_exo",
                )
                .prefetch_related("item__localizedname_set", "color__localizedname_set")
                .order_by("item__game_id", "-time")
                .distinct("item__game_id")
            )
            if colors.count() == 0:
                colors = None

        return colors

    def _get_color_groups(self, world, default=False):
        colors = self._get_colors(world, default)

        color_groups: dict[str, list] = {}
        if colors is not None:
            for group_name in settings.BOUNDLESS_WORLD_POLL_GROUP_ORDER:
                color_groups[group_name] = []

            for color in colors:
                item_id = color.item.game_id
                group_name = settings.BOUNDLESS_WORLD_POLL_COLOR_GROUPINGS[item_id]

                order_index = list(
                    settings.BOUNDLESS_WORLD_POLL_GROUP_ORDER[group_name]
                ).index(item_id)
                color_group: list[tuple[int, str]] = color_groups[group_name]
                color_group.append((order_index, color))
                color_groups[group_name] = color_group

            for group_name in list(color_groups.keys()):
                if len(color_groups[group_name]) == 0:
                    del color_groups[group_name]
                    continue

                color_groups[group_name] = [
                    c[1] for c in sorted(color_groups[group_name], key=lambda g: g[0])
                ]

        return color_groups

    def _get_color_variants(self, world):
        from boundlexx.boundless.models import (  # pylint: disable=cyclic-import
            ItemColorVariant,
            WorldBlockColor,
        )

        colors = self._get_colors(world) or []
        default_colors: list[WorldBlockColor] = []
        if world.is_sovereign:
            default_colors = self._get_colors(world, default=True) or []

        colors = list(colors) + list(default_colors)
        variants = set()
        for wbc in colors:
            variant = ItemColorVariant.objects.filter(
                item=wbc.item, color=wbc.color
            ).first()

            if variant is not None:
                variants.add(variant)

        return list(variants)

    def _get_context(self, world, resources=None):
        if self._context is not None:
            return self._context

        color_groups = self._get_color_groups(world)
        default_color_groups = None
        if world.is_sovereign:
            default_color_groups = self._get_color_groups(world, default=True)

            if len(default_color_groups) == 0:
                default_color_groups = None

        if resources is None:
            resources = self._get_resources(world)

        context = {
            "world": world,
            "color_groups": color_groups,
            "default_color_groups": default_color_groups,
        }
        if resources is not None and not world.is_creative:
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

    def _template(self, world, template, resources=None, extra=None):
        context = self._get_context(world, resources)
        if extra is not None:
            context.update(extra)

        message = ""

        message = render_to_string(
            template,
            context,
        )

        return self._markdown_replace(message)

    def _get_world_images(self, ids):
        from boundlexx.boundless.models import World  # pylint: disable=cyclic-import

        worlds = World.objects.filter(id__in=ids)
        world_images: dict[str, str] = {}

        for world in worlds:
            world_images[str(world.id)] = world.image.url

        return world_images

    def _get_forum_image_dict(self, image_type, use_forum_links=True, lookup_ids=None):
        image_dict = {}

        world_images: Optional[dict[str, str]] = None

        forum_images = ForumImage.objects.filter(image_type=image_type)
        if lookup_ids is not None:
            forum_images = forum_images.filter(lookup_id__in=lookup_ids)

        for image in forum_images:
            if use_forum_links:
                image_dict[image.lookup_id] = image.shortcut_url
            elif image_type == ForumImage.ImageType.WORLD:
                if world_images is None:
                    world_images = self._get_world_images(
                        [f.lookup_id for f in forum_images]
                    )
                image_dict[image.lookup_id] = world_images[image.lookup_id]
            else:
                image_dict[image.lookup_id] = image.url

        return image_dict

    def _upload_log(self, message):
        if os.environ.get("NOTIFICATION_PRINT"):
            print(message)
        else:
            logger.info(message)

    def _crop_image(self, image_file, size):
        img = Image.open(image_file.name)

        # crop to bounding box
        x1, y1, x2, y2 = img.getbbox()
        img = img.crop((x1 - 5, y1 - 5, x2 + 5, y2 + 5))
        img = img.crop(img.getbbox())

        # make square
        x, y = img.size
        width = max(x, y)
        new_img = Image.new("RGBA", (width, width), (0, 0, 0, 0))
        new_img.paste(img, (int((width - x) / 2), int((width - y) / 2)))

        # shrink size
        new_img.thumbnail((size, size), Image.LANCZOS)
        new_img.save(image_file.name, format="PNG")

    def _upload_forum_image(self, image_url, image_type, lookup_id, size=None):
        client = get_forum_client()

        temp_file = download_image(image_url)
        if size is not None:
            self._crop_image(temp_file, size)

        kwargs = {
            "type": "composer",
            "synchronous": "true",
        }

        with open(temp_file.name, "rb") as upload_file:
            # upload_image does not properly close file...
            forum_response = client._post(  # pylint: disable=protected-access
                "/uploads.json",
                files={"file": upload_file},
                **kwargs,
            )

        os.remove(temp_file.name)

        forum_image = ForumImage.objects.create(
            image_type=image_type,
            lookup_id=lookup_id,
            url=image_url,
            shortcut_url=forum_response["short_url"],
        )
        forum_image.save()

        return forum_image.shortcut_url

    def _upload_item_image(self, variant):
        self._upload_log(f"Uploading item image to the forums: {variant.image.url}")

        return self._upload_forum_image(
            variant.image.url,
            ForumImage.ImageType.ITEM,
            variant.lookup_id,
            size=30,
        )

    def _upload_world_image(self, world):
        self._upload_log(f"Uploading world image to the forums: {world.image.url}")

        return self._upload_forum_image(
            world.image.url,
            ForumImage.ImageType.WORLD,
            world.id,
        )

    def _get_resources(self, world):
        from boundlexx.boundless.models import (  # pylint: disable=cyclic-import
            WorldPoll,
        )

        wp = WorldPoll.objects.filter(world=world).order_by("time").first()
        if wp is not None:
            return wp.resources
        return None

    def forum(
        self, world, resources=None, extra=None
    ):  # pylint: disable=arguments-differ

        use_forum_links = True
        if extra is not None:
            use_forum_links = extra.get("forum_links", True)

        special_type = ""
        if world.special_type is not None and world.special_type > 0:
            special_type = f"{world.get_special_type_display()} "

        title = (
            f"[{world.display_name}] "
            f"--[{world.get_tier_display()} {world.get_world_type_display()} "
            f"{special_type}{world.world_class}]-- "
            f"[{'Active' if world.active else 'Inactive'}]"
        )

        variants = self._get_color_variants(world)

        extra_context = {
            "color_images": self._get_forum_image_dict(
                ForumImage.ImageType.COLOR, use_forum_links=use_forum_links
            ),
            "world_images": self._get_forum_image_dict(
                ForumImage.ImageType.WORLD, use_forum_links=use_forum_links
            ),
            "world_type_images": self._get_forum_image_dict(
                ForumImage.ImageType.TYPE, use_forum_links=use_forum_links
            ),
            "atmosphere_images": self._get_forum_image_dict(
                ForumImage.ImageType.ATMOSPHERE, use_forum_links=use_forum_links
            ),
            "misc_images": self._get_forum_image_dict(
                ForumImage.ImageType.MISC, use_forum_links=use_forum_links
            ),
            "item_images": self._get_forum_image_dict(
                ForumImage.ImageType.ITEM,
                use_forum_links=use_forum_links,
                lookup_ids=[v.lookup_id for v in variants],
            ),
            "cdn_item_images": self._get_forum_image_dict(
                ForumImage.ImageType.ITEM,
                use_forum_links=False,
                lookup_ids=[v.lookup_id for v in variants],
            ),
        }

        if (
            world.image is not None
            and world.image.name
            and str(world.id) not in extra_context["world_images"]
        ):
            if use_forum_links:
                extra_context["world_images"][world.id] = self._upload_world_image(
                    world
                )
            else:
                extra_context["world_images"][world.id] = world.image.url

        for variant in variants:
            if variant.lookup_id not in extra_context["item_images"]:
                if use_forum_links:
                    extra_context["item_images"][
                        variant.lookup_id
                    ] = self._upload_item_image(variant)
                else:
                    extra_context["item_images"][variant.lookup_id] = variant.image.url
                extra_context["cdn_item_images"][variant.lookup_id] = variant.image.url

        if extra is not None:
            extra_context.update(extra)

        return (
            world,
            title,
            self._template(
                world,
                "boundlexx/notifications/forum.md",
                resources=resources,
                extra=extra_context,
            ),
        )

    def _main_embed(self, world, is_update=False):
        files: Optional[dict[str, str]] = None

        main_embed: dict[str, Any] = {
            "fields": [
                {
                    "name": "🌍 World Details",
                    "value": (f"\n\n**ID**: {world.id}\n"),
                }
            ]
        }

        if world.special_type is not None and world.special_type > 0:
            main_embed["fields"][0][
                "value"
            ] += f"**Special Type**: {world.get_special_type_display()}\n"

        main_embed["fields"][0]["value"] += (
            f"**Type**: {world.get_world_type_display()}\n"
            f"**Tier**: {world.get_tier_display()}\n"
            f"**Atmosphere**: {world.protection or 'Normal'}\n"
            f"**Size**: {world.display_size}\n"
            f"**Liquid**: ▲ {world.surface_liquid} | "
            f"▼ {world.core_liquid}\n"
            f"**Region**: {world.get_region_display()}\n"
        )
        main_embed["title"] = world.display_name

        if is_update:
            main_embed[
                "description"
            ] = f"New information is avaiable for this {self._world_type}!"
        else:
            main_embed["description"] = f"A new {self._world_type} has appeared!"

        if world.forum_url:
            main_embed["url"] = world.forum_url

        if world.image.name:
            main_embed["thumbnail"] = {"url": f"attachment://{world.image.name}"}

            files = {world.image.name: world.image.url}

        if world.assignment is not None:
            main_embed["fields"].append(
                {
                    "name": "🧭 Distance Details",
                    "value": (
                        f"**{world.assignment_distance} blinksecs** from "
                        f"**{world.assignment}** (cost: **{world.assignment_cost}c**)"
                    ),
                }
            )

        if world.start is not None:
            timestring = (
                f"Appeared {naturaltime(world.start)} ({world.start.isoformat()})"
            )
            if world.end is not None:
                timestring += (
                    f"\nLast until {naturaltime(world.end)} ({world.end.isoformat()})"
                )

            main_embed["fields"].append(
                {
                    "name": "⏱ Time Details",
                    "value": timestring,
                },
            )

        return main_embed, files

    def _resource_embed(self, embedded_resources, surface_resources):
        resource_embed: dict = {"title": "World Resources"}
        fields: list[dict[str, str]] = []

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

    def _color_embed(self, world, color_groups):
        color_embed: dict = {"title": "Block Colors"}
        fields: list[dict[str, str]] = []
        for group_name, color_group in color_groups.items():
            value = ""
            for color in color_group:
                value += (
                    f"\n* **{color.item.english}**: "
                    f"_{color.color.default_name} ({color.color.game_id})_"
                )

                extra = []
                if world.is_exo:
                    if color.is_new_exo:
                        extra.append("**NEW**")
                    elif color.is_new:
                        if color.transform_first_world is not None:
                            extra.append("**TRANS**")
                        if color.transform_last_exo is not None:
                            extra.append("**EXOTRANS**")
                        if color.days_since_exo:
                            extra.append(f"**Days: {color.days_since_exo}**")
                elif world.is_sovereign and not world.is_creative:
                    if color.is_new and color.is_default:
                        extra.append("**NEW**")

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

        if not world.is_creative and resources is not None:
            resource_embed = self._resource_embed(
                context["embedded_resources"], context["surface_resources"]
            )
            if resource_embed is not None:
                embeds.append(resource_embed)

        if world.special_type != 1:
            color_embed = self._color_embed(world, context["color_groups"])
            if color_embed is not None:
                embeds.append(color_embed)

        return embeds, files


class ExoworldNotification(ExportModelOperationsMixin("exoworld_notification"), WorldNotification):  # type: ignore # noqa E501
    _world_type = "exoworld"


class ExoworldExpiredNotification(ExportModelOperationsMixin("exoworld_expired_notification"), WorldNotification):  # type: ignore # noqa E501
    _world_type = "exoworld"


class SovereignWorldNotification(ExportModelOperationsMixin("sovereign_world_notification"), WorldNotification):  # type: ignore # noqa E501
    _world_type = "sovereign world"


class CreativeWorldNotification(ExportModelOperationsMixin("createive_world_notification"), WorldNotification):  # type: ignore # noqa E501
    _world_type = "creative world"


class HomeworldNotification(ExportModelOperationsMixin("homeworld_notification"), WorldNotification):  # type: ignore # noqa E501
    _world_type = "homeworld"


class SovereignColorNotification(ExportModelOperationsMixin("sovereign_color_notification"), NotificationBase):  # type: ignore # noqa E501
    objects = PolymorphicNotificationManager()

    def embed(self, item, colors, new_ids):  # pylint: disable=arguments-differ
        lines = []
        fields = []

        title = "Color Details"
        colors = sorted(colors, key=lambda c: c.game_id)
        for color in colors:
            line = f"_{color.default_name} ({color.game_id})_"

            if color.game_id in new_ids:
                line += " **NEW**"
            lines.append(line)

            if len(lines) == 40:
                fields.append(
                    {
                        "name": title,
                        "value": "\n".join(lines),
                    }
                )

                title = "cont'd"
                lines = []

        fields.append(
            {
                "name": title,
                "value": "\n".join(lines),
            }
        )

        main_embed: dict[str, Any] = {
            "title": item.english,
            "description": "New Sovereign selectable colors found!",
            "fields": fields,
        }

        return [main_embed], None


class FailedTaskNotificationManager(PolymorphicManager):
    def send_notification(self, task, exc=None):
        notifications = self.filter(active=True)

        messages = render_discord_messages(is_huey=exc is not None, task=task, exc=exc)
        for notification in notifications:
            if not isinstance(notification.subscription, DiscordWebhookSubscription):
                raise ValueError(
                    "Only DiscordWebhookSubscription as for this notification type"
                )

            send_discord_webhook(notification.subscription.webhook_url, messages)


class FailedTaskNotification(ExportModelOperationsMixin("failed_task_notification"), NotificationBase):  # type: ignore # noqa E501
    objects = FailedTaskNotificationManager()


@receiver(post_save, sender=TaskResult)
def task_failure_handler(sender, instance, **kwargs):
    if (
        instance.status == "FAILURE"
        and instance.task_name != "boundlexx.notifications.tasks.send_discord_webhook"
    ):
        FailedTaskNotification.objects.send_notification(instance)
