from __future__ import annotations

from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from boundlexx.boundless.client import BoundlessClient
from boundlexx.boundless.models.game import Color, Item
from boundlexx.boundless.utils import (
    convert_linear_rgb_to_hex,
    get_next_rank_update,
)
from boundlexx.notifications.models import ExoworldNotification

PORTAL_CONDUITS = [2, 3, 4, 6, 8, 10, 15, 18, 24]


class WorldManager(models.Manager):
    def get_and_replace_expired_exo(self, world_id, display_name, end):
        end_lower = end - timedelta(days=1)
        end_upper = end + timedelta(days=1)

        old_world = World.objects.filter(
            display_name=display_name,
            id__gte=settings.BOUNDLESS_EXO_EXPIRED_BASE_ID,
            end__gte=end_lower,
            end__lte=end_upper,
            owner__isnull=True,
        ).first()

        if old_world is not None:
            old_id = old_world.id

            world = old_world
            world.id = world_id
            world.active = True
            world.save()

            WorldBlockColor.objects.filter(world_id=old_id).update(
                world_id=world.id
            )
            World.objects.filter(id=old_id).delete()

            return world
        return None

    def get_or_create_from_game_dict(self, world_dict):
        created = False

        world = self.filter(id=world_dict["id"]).first()

        start = None
        end = None
        if "lifetime" in world_dict:
            start = datetime.utcfromtimestamp(
                world_dict["lifetime"][0]
            ).replace(tzinfo=pytz.utc)
            end = datetime.utcfromtimestamp(world_dict["lifetime"][1]).replace(
                tzinfo=pytz.utc
            )

        if world is None and end is not None:
            world = self.get_and_replace_expired_exo(
                world_dict["id"], world_dict["displayName"], end
            )

        if world is None:
            world = World.objects.create(
                id=world_dict["id"],
                display_name=world_dict["displayName"],
            )
            created = True

        created = created or world.address is None

        world.display_name = world_dict["displayName"]
        world.name = world_dict["name"]
        world.region = world_dict["region"]
        world.tier = world_dict["tier"]
        world.size = world_dict["worldSize"]
        if settings.BOUNDLESS_TESTING_FEATURES:
            world.world_type = settings.BOUNDLESS_WORLD_TYPE_MAPPING.get(
                world_dict["worldType"]
            )
            world.description = None
        else:
            world.world_type = world_dict["worldType"]
            world.description = world_dict["worldDescription"]
        world.time_offset = datetime.utcfromtimestamp(
            world_dict["timeOffset"]
        ).replace(tzinfo=pytz.utc)
        world.atmosphere_color_r = world_dict["atmosphereColor"][0]
        world.atmosphere_color_g = world_dict["atmosphereColor"][1]
        world.atmosphere_color_b = world_dict["atmosphereColor"][2]
        world.water_color_r = world_dict["waterColor"][0]
        world.water_color_g = world_dict["waterColor"][1]
        world.water_color_b = world_dict["waterColor"][2]
        world.address = world_dict.get("addr")
        world.ip_address = world_dict.get("ipAddr")
        world.api_url = world_dict.get("apiURL")
        world.websocket_url = world_dict.get("websocketURL")
        world.is_creative = world_dict.get("creative", False)
        world.owner = world_dict.get("owner", None)
        world.assignment_id = world_dict.get("assignment", None)
        world.is_locked = world_dict.get("locked", False)
        world.is_public = world_dict.get("public", True)
        world.number_of_regions = world_dict["numRegions"]
        world.active = True

        if start is not None:
            world.start = start

        if end is not None:
            world.end = end

        world.save()

        return world, created

    def get_or_create_forum_world(self, forum_id, world_info):
        created = False

        # see if world exists that was created by this method before
        world = self.filter(forum_id=forum_id).first()

        # else, see if world exist from elsewhere
        if world is None:
            world = self.filter(
                display_name=world_info["name"],
                owner__isnull=True,
                active=True,
            ).first()

            # wrong world, this one comes from another forum post
            if world is not None and world.forum_id is not None:
                world = None

        # otherwise, create it
        if world is None:
            world, created = self.get_or_create(
                id=settings.BOUNDLESS_EXO_EXPIRED_BASE_ID + forum_id,
                display_name=world_info["name"],
            )

        if "tier" in world_info and world.tier is None:
            world.tier = world_info["tier"]
        if "type" in world_info and world.world_type is None:
            world.world_type = world_info["type"]

            if world.world_type == "UMBRIS":
                world.world_type = "DARKMATTER"
        if "start" in world_info and world.start is None:
            world.start = world_info["start"]
        if "end" in world_info and world.end is None:
            world.end = world_info["end"]
        if "server" in world_info and world.region is None:
            world.region = world_info["server"]

        new_data = False
        if "image" in world_info and (
            world.image is None or not world.image.name
        ):
            world.image = world_info["image"]
            new_data = True
        if world.forum_id is None:
            world.forum_id = forum_id
            new_data = True

        if new_data:
            ExoworldNotification.objects.send_update_notification(world)

        world.save()

        return world, created


class World(ExportModelOperationsMixin("world"), models.Model):  # type: ignore
    objects = WorldManager()

    class Region(models.TextChoices):
        REGION_USE = "use", _("US East")
        REGION_USW = "usw", _("US West")
        REGION_EUC = "euc", _("EU Central")
        REGION_AUS = "aus", _("Australia")
        REGION_CREATIVE = "sandbox", _("Sandbox")

    class Tier(models.IntegerChoices):
        TIER_1 = 0, _("Placid (1)")
        TIER_2 = 1, _("Temperate (2)")
        TIER_3 = 2, _("Rugged (3)")
        TIER_4 = 3, _("Inhospitable (4)")
        TIER_5 = 4, _("Turbulent (5)")
        TIER_6 = 5, _("Fierce (6)")
        TIER_7 = 6, _("Savage (7)")
        TIER_8 = 7, _("Brutal (8)")

    class WorldType(models.TextChoices):
        TYPE_LUSH = "LUSH", _("Lush")
        TYPE_METAL = "METAL", _("Metal")
        TYPE_COAL = "COAL", _("Coal")
        TYPE_CORROSIVE = "CORROSIVE", _("Corrosive")
        TYPE_SHOCK = "SHOCK", _("Shock")
        TYPE_BLAST = "BLAST", _("Blast")
        TYPE_TOXIC = "TOXIC", _("Toxic")
        TYPE_CHILL = "CHILL", _("Chill")
        TYPE_BURN = "BURN", _("Burn")
        TYPE_UMBRIS = "DARKMATTER", _("Umbris")
        TYPE_RIFT = "RIFT", _("Rift")
        TYPE_BLINK = "BLINK", _("Blink")

    class Meta:
        ordering = ["id"]
        indexes = [
            GinIndex(fields=["name"]),
            GinIndex(fields=["display_name"]),
        ]

    name = models.CharField(_("Name"), max_length=64, null=True, db_index=True)
    display_name = models.CharField(
        _("Display Name"), max_length=64, db_index=True
    )
    region = models.CharField(
        _("Server Region"),
        max_length=16,
        choices=Region.choices,
        null=True,
        db_index=True,
        help_text=_("Server Region"),
    )
    tier = models.PositiveSmallIntegerField(
        _("Tier"),
        choices=Tier.choices,
        null=True,
        db_index=True,
        help_text=_("Tier of the world. Starts at 0."),
    )
    description = models.CharField(_("Description"), max_length=32, null=True)
    size = models.IntegerField(_("World Size"), null=True)
    world_type = models.CharField(
        _("World Type"),
        choices=WorldType.choices,
        max_length=10,
        null=True,
        db_index=True,
    )
    address = models.CharField(
        _("Server Address"), max_length=128, blank=True, null=True
    )
    ip_address = models.GenericIPAddressField(
        _("Server IP Address"), blank=True, null=True
    )
    api_url = models.URLField(_("API URL"), blank=True, null=True)
    planets_url = models.URLField(_("Planets URL"), blank=True, null=True)
    chunks_url = models.URLField(_("Chunks URL"), blank=True, null=True)
    time_offset = models.DateTimeField(_("Time Offset"), null=True)
    websocket_url = models.URLField(_("Websocket URL"), blank=True, null=True)
    assignment = models.ForeignKey(
        "World",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("The world this planet orbits, if any"),
    )
    owner = models.PositiveSmallIntegerField(blank=True, null=True)
    is_creative = models.BooleanField(
        default=False,
        db_index=True,
        null=True,
        help_text=_("If the world is a creative one"),
    )
    is_locked = models.BooleanField(
        default=False,
        db_index=True,
        null=True,
        help_text=_(
            "If this world is locked (only `true` for Soverign worlds)"
        ),
    )
    is_public = models.BooleanField(
        default=True,
        db_index=True,
        null=True,
        help_text=_("If this world is public"),
    )
    number_of_regions = models.PositiveSmallIntegerField(blank=True, null=True)

    atmosphere_color_r = models.FloatField(
        _("Atmosphere Linear R Color"), null=True
    )
    atmosphere_color_g = models.FloatField(
        _("Atmosphere Linear G Color"), null=True
    )
    atmosphere_color_b = models.FloatField(
        _("Atmosphere Linear B Color"), null=True
    )
    water_color_r = models.FloatField(_("Water Linear R Color"), null=True)
    water_color_g = models.FloatField(_("Water Linear G Color"), null=True)
    water_color_b = models.FloatField(_("Water Linear B Color"), null=True)

    forum_id = models.PositiveIntegerField(null=True, blank=True)

    active = models.BooleanField(default=True, db_index=True)

    start = models.DateTimeField(blank=True, null=True, db_index=True)
    end = models.DateTimeField(blank=True, null=True, db_index=True)

    image = models.ImageField(blank=True, null=True)
    exo_notification_sent = models.NullBooleanField()

    def __str__(self):
        return self.display_name

    @property
    def is_perm(self):
        if self.id >= settings.BOUNDLESS_EXO_EXPIRED_BASE_ID:
            return False
        return self.end is None

    @property
    def is_sovereign(self):
        return self.owner is not None

    @property
    def is_exo(self):
        return self.owner is None and not self.is_perm

    @property
    def atmosphere_color(self):
        if (
            self.atmosphere_color_r is None
            or self.atmosphere_color_g is None
            or self.atmosphere_color_b is None
        ):
            return None

        return convert_linear_rgb_to_hex(
            self.atmosphere_color_r,
            self.atmosphere_color_g,
            self.atmosphere_color_b,
        )

    @property
    def water_color(self):
        if (
            self.water_color_r is None
            or self.water_color_g is None
            or self.water_color_g is None
        ):
            return None

        return convert_linear_rgb_to_hex(
            self.water_color_r,
            self.water_color_g,
            self.water_color_g,
        )

    @property
    def protection(self):
        if self.tier is None or self.tier < World.Tier.TIER_4:
            return None

        points = "5 points + Pie"
        amount = 10
        if self.tier == World.Tier.TIER_4:
            amount = 1
            points = "1 points"
        elif self.tier == World.Tier.TIER_5:
            amount = 3
            points = "3 points"
        elif self.tier == World.Tier.TIER_6:
            amount = 5
            points = "4 points"
        elif self.tier == World.Tier.TIER_7:
            amount = 7
            points = "5 points"

        protection_type = "Volatile"
        if self.world_type in (
            World.WorldType.TYPE_LUSH,
            World.WorldType.TYPE_CORROSIVE,
            World.WorldType.TYPE_TOXIC,
            World.WorldType.TYPE_UMBRIS,
        ):
            protection_type = "Caustic"
        elif self.world_type in (
            World.WorldType.TYPE_METAL,
            World.WorldType.TYPE_SHOCK,
            World.WorldType.TYPE_CHILL,
            World.WorldType.TYPE_RIFT,
        ):
            protection_type = "Potent"

        return f"Lvl {amount} {protection_type} ({points})"

    @property
    def surface_liquid(self):
        key = "DEFAULT"
        if (
            self.world_type is not None
            and self.world_type in settings.BOUNDLESS_WORLD_LIQUIDS
        ):
            key = self.world_type
        return settings.BOUNDLESS_WORLD_LIQUIDS[key][0]

    @property
    def core_liquid(self):
        key = "DEFAULT"
        if (
            self.world_type is not None
            and self.world_type in settings.BOUNDLESS_WORLD_LIQUIDS
        ):
            key = self.world_type
        return settings.BOUNDLESS_WORLD_LIQUIDS[key][1]

    def _get_distance_to_world(self, world, client=None):
        distance_obj = WorldDistance.objects.filter(
            models.Q(world_source=self, world_dest=world)
            | models.Q(world_source=world, world_dest=self)
        ).first()

        distance = 0.0
        if distance_obj is None:
            if world.id != self.id:
                if client is None:
                    client = BoundlessClient()

                distance = client.get_world_distance(self.id, world.id)
                # value is returned as a float, no idea how cost formula works
                # with non-whole numbers
                if distance is not None and not distance.is_integer():
                    raise ValueError(
                        "Unexpected distance number: "
                        f"{self.id} to {world.id} = {distance}"
                    )

            distance_obj = WorldDistance.objects.create(
                world_source=self, world_dest=world, distance=int(distance)
            )

        return distance_obj

    def get_distance_to_world(self, world, client=None):
        distance_obj = self._get_distance_to_world(world, client=client)

        return distance_obj.distance

    @cached_property
    def assignment_distance(self):
        if self.assignment is None:
            return None

        # if distance is partial, lets not blow up the exo world task
        try:
            return self.get_distance_to_world(self.assignment)
        except ValueError:
            return None

    @cached_property
    def assignment_cost(self):
        if self.assignment is None:
            return None

        # if distance is partial, lets not blow up the exo world task
        try:
            distance_obj = self._get_distance_to_world(self.assignment)
        except ValueError:
            return None
        return distance_obj.cost

    @property
    def forum_url(self):
        if self.forum_id is None:
            return None

        return f"{settings.BOUNDLESS_FORUM_BASE_URL}/t/{self.forum_id}"

    @property
    def next_shop_stand_update(self):
        return get_next_rank_update(self.itemsellrank_set.all())

    @property
    def next_request_basket_update(self):
        return get_next_rank_update(self.itembuyrank_set.all())


class WorldDistance(
    ExportModelOperationsMixin("world_distance"), models.Model  # type: ignore
):
    world_source = models.ForeignKey(
        World, on_delete=models.CASCADE, related_name="+"
    )
    world_dest = models.ForeignKey(
        World, on_delete=models.CASCADE, related_name="+"
    )
    distance = models.PositiveSmallIntegerField(
        _("Distance to work in blinksecs")
    )

    @cached_property
    def cost(self):
        if self.distance < 13:
            return 100 + max(self.distance - 1, 0) * 80

        remaining = max(self.distance - 14, 0)
        multiplier = remaining // 5
        extra = remaining % 5
        return 1100 + multiplier * 400 + extra * 100

    @cached_property
    def min_portal_cost(self):
        if (
            self.world_source.is_exo
            or self.world_dest.is_exo
            or self.distance > 25
        ):
            return None

        if self.distance < 3:
            return 1
        if self.distance < 5:
            return 2

        return min((self.distance - 5) // 3 + 3, 9)

    @cached_property
    def min_portal_open_cost(self):
        if self.min_portal_cost is None:
            return None

        return self.min_portal_cost * 50

    @cached_property
    def min_conduits(self):
        if self.min_portal_cost is None:
            return None

        return PORTAL_CONDUITS[self.min_portal_cost - 1]


class WorldBlockColorManager(models.Manager):
    def get_or_create_color(self, world, item, color):
        created = False
        block_color = self.filter(world=world, item=item, active=True).first()

        if block_color is None or (
            world.owner is not None and block_color.color != color
        ):
            if world.owner is not None:
                self.filter(world=world, item=item, active=True).update(
                    active=False
                )

            created = True
            block_color = self.create(
                world=world, item=item, color=color, active=True
            )
        elif block_color.color != color:
            block_color.color = color
            block_color.save()

        return block_color, created


class WorldBlockColor(
    ExportModelOperationsMixin("world_block_color"), models.Model  # type: ignore # noqa E501
):
    objects = WorldBlockColorManager()

    world = models.ForeignKey(World, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    _new_color = models.NullBooleanField()
    _exist_on_perm = models.NullBooleanField()
    _exist_via_transform = models.NullBooleanField()
    _days_since_last = models.IntegerField(null=True, blank=True)

    @property
    def exist_on_perm(self):
        if self._exist_on_perm is None:
            if self.world.end is None:
                exist_on_perm = True
            else:
                exist_on_perm = (
                    WorldBlockColor.objects.filter(
                        item=self.item,
                        color=self.color,
                        world__end__isnull=True,
                    ).count()
                    > 0
                )
            self._exist_on_perm = exist_on_perm
            self.save()
        return self._exist_on_perm

    @property
    def is_new_color(self):
        if self._new_color is None:
            if self.exist_on_perm:
                new_color = False
            elif self.world.end is None:
                new_color = True
            else:
                new_color = (
                    WorldBlockColor.objects.filter(
                        item=self.item,
                        color=self.color,
                        world__end__isnull=False,
                        world__end__lt=self.world.start,
                    ).count()
                    == 0
                )

            self._new_color = new_color
            self.save()
        return self._new_color

    @property
    def transform_group(self):
        return settings.BOUNDLESS_TRANSFORMATION_GROUPS.get(self.item.game_id)

    @property
    def exist_via_transform(self):
        if self._exist_via_transform is None:
            if self.transform_group is None or self.exist_on_perm:
                return None

            if (
                WorldBlockColor.objects.filter(
                    item=self.item,
                    color=self.color,
                    world__end__isnull=True,
                ).count()
                > 0
            ):
                exist_via_transform = False

            exist_via_transform = (
                WorldBlockColor.objects.filter(
                    item__game_id__in=self.transform_group,
                    color=self.color,
                    world__end__isnull=True,
                ).count()
                > 0
            )

            self._exist_via_transform = exist_via_transform
            self.save()
        return self._exist_via_transform

    @property
    def days_since_last(self):
        if self._days_since_last == -1:
            return None
        if self._days_since_last is not None:
            return self._days_since_last

        if self._new_color:
            return None

        self._days_since_last = -1

        # color exists on perm world
        if (
            WorldBlockColor.objects.filter(
                item=self.item, color=self.color, world__end__isnull=True
            ).count()
            == 0
        ):
            last = (
                WorldBlockColor.objects.filter(
                    item=self.item,
                    color=self.color,
                    world__owner__isnull=True,
                    world__is_creative=False,
                    world__end__isnull=False,
                    world__end__lt=self.world.start,
                )
                .order_by("-world__end")
                .first()
            )

            self._days_since_last = (
                self.world.start - last.world.end  # type: ignore
            ).days
        self.save()

        if self._days_since_last == -1:
            return None
        return self._days_since_last


class WorldCreatureColor(
    ExportModelOperationsMixin("world_creature_color"), models.Model  # type: ignore  # noqa E501
):
    class CreatureType(models.TextChoices):
        CUTTLETRUNK = "CUTTLETRUNK", _("Cuttletrunk")
        HOPPER = "HOPPER", _("Hopper")
        HUNTER = "HUNTER", _("Hunter")
        ROADRUNNER = "ROADRUNNER", _("Roadrunner")
        SPITTER = "SPITTER", _("Spitter")
        WILDSTOCK = "WILDSTOCK", _("Wildstock")

    world = models.ForeignKey(World, on_delete=models.CASCADE)
    creature_type = models.CharField(
        max_length=16, choices=CreatureType.choices
    )
    color_data = models.TextField()

    class Meta:
        unique_together = ("world", "creature_type")


class WorldPollManager(models.Manager):
    def _create_resource_counts(self, world_poll, resources_list):
        resource_order = list(
            settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING.keys()
        )

        resources = []
        embedded_total = 0
        surface_total = 0

        for index, amount in enumerate(resources_list):
            if amount == 0:
                continue

            item_id = resource_order[index]
            resources.append((item_id, amount))

            if settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING[item_id]:
                embedded_total += amount
            else:
                surface_total += amount

        for item_data in resources:
            item_id, amount = item_data[0], item_data[1]

            item = Item.objects.get(game_id=item_id)

            if settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING[item_id]:
                total = embedded_total
            else:
                total = surface_total

            ResourceCount.objects.create(
                world_poll=world_poll,
                item=item,
                count=amount,
                percentage=(amount / total) * 100,
            )

    def create_from_game_dict(
        self, world_dict, poll_dict, world=None, new_world=False
    ):
        if world is None:
            world, new_world = World.objects.get_or_create_from_game_dict(
                world_dict
            )

        world_poll = self.create(world=world)

        WorldPollResult.objects.create(
            world_poll=world_poll,
            player_count=world_dict["info"]["players"],
            beacon_count=poll_dict["beacons"],
            plot_count=poll_dict["plots"],
            total_prestige=poll_dict.get("prestige"),
        )

        self._create_resource_counts(world_poll, poll_dict["resources"])

        for rank, leader in enumerate(poll_dict["leaderboard"]):
            rank += 1

            LeaderboardRecord.objects.create(
                world_poll=world_poll,
                world_rank=rank,
                guild_tag=leader["mayor"].get("guildTag", ""),
                mayor_id=leader["mayor"]["id"],
                mayor_name=leader["mayor"]["name"],
                mayor_type=leader["mayor"]["type"],
                name=leader["name"],
                prestige=leader["prestige"],
            )

        world_poll.refresh_from_db()

        new_world = (
            new_world or self.filter(world_id=world_poll.world_id).count() == 1
        )
        if new_world and world.is_exo:
            ExoworldNotification.objects.send_new_notification(world_poll)

        return world_poll


class WorldPoll(ExportModelOperationsMixin("world_poll"), models.Model):  # type: ignore # noqa E501
    objects = WorldPollManager()

    world = models.ForeignKey("World", on_delete=models.CASCADE)
    active = models.BooleanField(db_index=True, default=True)
    time = models.DateTimeField(auto_now_add=True)

    @property
    def result(self):
        return self.worldpollresult_set.first()

    @property
    def resources(self):
        return self.resourcecount_set.all()

    @property
    def leaderboard(self):
        return self.leaderboardrecord_set.all()


class WorldPollResult(
    ExportModelOperationsMixin("world_poll_result"), models.Model  # type: ignore # noqa E501
):
    time = models.DateTimeField(auto_now=True, primary_key=True)
    world_poll = models.ForeignKey("WorldPoll", on_delete=models.CASCADE)
    player_count = models.PositiveSmallIntegerField(_("Player Count"))
    beacon_count = models.PositiveIntegerField(_("Beacon Count"))
    plot_count = models.PositiveIntegerField(_("Plot Count"))
    total_prestige = models.PositiveIntegerField(
        _("Total Prestige"), blank=True, null=True
    )

    class Meta:
        unique_together = (
            "time",
            "world_poll",
        )


class ResourceCount(
    ExportModelOperationsMixin("resource_count"), models.Model  # type: ignore
):
    time = models.DateTimeField(auto_now=True, primary_key=True)
    world_poll = models.ForeignKey("WorldPoll", on_delete=models.CASCADE)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(_("Count"))
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = (
            "time",
            "world_poll",
            "item",
        )

        ordering = ["-count"]

    @cached_property
    def is_embedded(self):
        return settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING[
            self.item.game_id
        ]


class LeaderboardRecord(
    ExportModelOperationsMixin("leaderboard_record"), models.Model  # type: ignore # noqa E501
):
    time = models.DateTimeField(auto_now=True, primary_key=True)
    world_poll = models.ForeignKey("WorldPoll", on_delete=models.CASCADE)
    world_rank = models.PositiveSmallIntegerField(_("World Rank"))
    guild_tag = models.CharField(_("Guild Tag"), max_length=7)
    mayor_id = models.PositiveIntegerField()
    mayor_name = models.CharField(max_length=64)
    mayor_type = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=64)
    prestige = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            "time",
            "world_poll",
            "world_rank",
        )

        ordering = ["world_rank"]
