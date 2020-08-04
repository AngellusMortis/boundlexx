from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict

import pytz
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicManager, PolymorphicModel

from boundlexx.boundless.client import BoundlessClient, Location, ShopItem
from boundlexx.boundless.utils import convert_linear_rgb_to_hex, purge_cache
from boundlexx.notifications.models import ExoworldNotification


class GameObjManager(PolymorphicManager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("localizedname")


class GameObj(PolymorphicModel):
    active = models.BooleanField(_("Active"), default=True)
    game_id = models.IntegerField(_("Game ID"), db_index=True)

    class Meta:
        unique_together = ("game_id", "polymorphic_ctype")
        ordering = ["game_id"]

    def __str__(self):
        if self.default_name:
            return f"{self.game_id}: {self.default_name}"
        return str(self.game_id)

    @cached_property
    def localized_names(self):
        names = {}
        for name in self.localizedname_set.all():
            names[name.lang] = name.name
        return names

    @cached_property
    def localization_cache_key(self):
        return f"localized_name:{self.polymorphic_ctype_id}_{self.game_id}"

    @cached_property
    def default_name(self):
        localized_name = cache.get(self.localization_cache_key)

        if localized_name is None:
            localized_name = self.localized_names.get("english")
            cache.set(self.localization_cache_key, localized_name)
        return localized_name


class LocalizedName(PolymorphicModel):
    game_obj = models.ForeignKey(GameObj, on_delete=models.CASCADE)
    lang = models.CharField(_("Language"), max_length=16)
    name = models.CharField(_("Name"), max_length=128, db_index=True)

    class Meta:
        unique_together = ("game_obj", "lang")

    def __str__(self):
        return f"{self.lang}: {self.name}"


class Subtitle(GameObj):
    pass


class Color(GameObj):
    @cached_property
    def base_color(self):
        colors: Dict[int, int] = {}

        for color in self.colorvalue_set.all():
            color_count = colors.get(color.base, 0) + 1

            colors[color.base] = color_count

        base_color = None
        highest_count = -1
        for color_value, count in colors.items():
            if count > highest_count:
                highest_count = count
                base_color = color_value

        if base_color is None:
            return None

        return f"#{base_color:06x}"

    @cached_property
    def gleam_color(self):
        for color in self.colorvalue_set.all():
            if color.color_type == ColorValue.ColorType.GLEAM:
                return color.rgb_color
        return None


class ColorValue(models.Model):
    class ColorType(models.TextChoices):
        CHARACTER = "CHARACTER", _("CHARACTER")
        CHARACTER_DECAL = "CHARACTER_DECAL", _("CHARACTER_DECAL")
        CREATURE_BASE = "CREATURE_BASE", _("CREATURE_BASE")
        CREATURE_AUX = "CREATURE_AUX", _("CREATURE_AUX")
        CREATURE_EXOTIC = "CREATURE_EXOTIC", _("CREATURE_EXOTIC")
        WOOD = "WOOD", _("WOOD")
        ROCK = "ROCK", _("ROCK")
        GRASS = "GRASS", _("GRASS")
        ICE = "ICE", _("ICE")
        GLACIER = "GLACIER", _("GLACIER")
        SOIL = "SOIL", _("SOIL")
        ASH = "ASH", _("ASH")
        GLEAM = "GLEAM", _("GLEAM")
        GRAVEL = "GRAVEL", _("GRAVEL")
        GROWTH = "GROWTH", _("GROWTH")
        MOULD = "MOULD", _("MOULD")
        SAND = "SAND", _("SAND")
        SPONGE = "SPONGE", _("SPONGE")
        LEAVES = "LEAVES", _("LEAVES")
        MANTLE = "MANTLE", _("MANTLE")
        MUD = "MUD", _("MUD")
        TANGLE = "TANGLE", _("TANGLE")
        THORNS = "THORNS", _("THORNS")
        FLORA_1 = "FLORA_1", _("FLORA_1")
        FLORA_DECAL_1 = "FLORA_DECAL_1", _("FLORA_DECAL_1")
        FLORA_2 = "FLORA_2", _("FLORA_2")
        FLORA_DECAL_2 = "FLORA_DECAL_2", _("FLORA_DECAL_2")
        FLORA_3 = "FLORA_3", _("FLORA_3")
        FLORA_DECAL_3 = "FLORA_DECAL_3", _("FLORA_DECAL_3")
        FLORA_4 = "FLORA_4", _("FLORA_4")
        FLORA_DECAL_4 = "FLORA_DECAL_4", _("FLORA_DECAL_4")
        INK = "INK", _("INK")
        FIBER = "FIBER", _("FIBER")

    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    color_type = models.CharField(max_length=16, choices=ColorType.choices)
    shade = models.IntegerField()
    base = models.IntegerField()
    hlight = models.IntegerField()

    class Meta:
        unique_together = ("color", "color_type")

    @property
    def rgb_color(self):
        if self.base is None:
            return None
        return f"#{self.base:06x}"


class Metal(GameObj):
    pass


class Item(GameObj):
    item_subtitle = models.ForeignKey(
        Subtitle, on_delete=models.SET_NULL, blank=True, null=True
    )
    string_id = models.CharField(_("String ID"), max_length=64)

    @property
    def default_name(self):  # pylint: disable=invalid-overridden-method
        return self.string_id

    @property
    def english(self):
        return super().default_name

    @property
    def buy_locations(self):
        return self.itemshopstandprice_set.filter(active=True)

    @property
    def sell_locations(self):
        return self.itemrequestbasketprice_set.filter(active=True)

    @property
    def is_resource(self):
        return self.game_id in settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING

    @property
    def has_colors(self):
        return self.worldblockcolor_set.count() > 0


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
                id=world_dict["id"], display_name=world_dict["displayName"],
            )
            created = True

        created = created or world.address is None

        world.name = world_dict["name"]
        world.region = world_dict["region"]
        world.tier = world_dict["tier"]
        world.description = world_dict["worldDescription"]
        world.size = world_dict["worldSize"]
        world.world_type = world_dict["worldType"]
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

        if start is not None:
            world.start = start
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
        if "start" in world_info and world.start is None:
            world.start = world_info["start"]
        if "end" in world_info and world.end is None:
            world.end = world_info["end"]
        if "server" in world_info and world.region is None:
            world.region = world_info["server"]
        if world.forum_id is None:
            world.forum_id = forum_id

        world.save()

        return world, created


class World(models.Model):
    objects = WorldManager()

    class Region(models.TextChoices):
        REGION_USE = "use", _("US East")
        REGION_USW = "usw", _("US West")
        REGION_EUC = "euc", _("EU Central")
        REGION_AUS = "aus", _("Australia")
        REGION_CREATIVE = "creative", _("Creative")

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
        TYPE_UMBRIS = "UMBRIS", _("Umbris")
        TYPE_RIFT = "RIFT", _("Rift")
        TYPE_BLINK = "BLINK", _("Blink")

    class Meta:
        ordering = ["id"]

    name = models.CharField(_("Name"), max_length=64, null=True)
    display_name = models.CharField(_("Display Name"), max_length=64)
    region = models.CharField(
        _("Server Region"), max_length=16, choices=Region.choices, null=True
    )
    tier = models.PositiveSmallIntegerField(
        _("Tier"), choices=Tier.choices, null=True
    )
    description = models.CharField(_("Description"), max_length=32, null=True)
    size = models.IntegerField(_("World Size"), null=True)
    world_type = models.CharField(
        _("World Type"), choices=WorldType.choices, max_length=9, null=True
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
        "World", on_delete=models.CASCADE, blank=True, null=True
    )
    owner = models.PositiveSmallIntegerField(blank=True, null=True)
    is_creative = models.BooleanField(default=False, db_index=True, null=True)
    is_locked = models.BooleanField(default=False, db_index=True, null=True)
    is_public = models.BooleanField(default=True, db_index=True, null=True)
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

    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

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
            self.water_color_r, self.water_color_g, self.water_color_g,
        )

    @property
    def protection(self):
        if self.tier is None or self.tier < World.Tier.TIER_4:
            return None

        amount = 5
        if self.tier == World.Tier.TIER_4:
            amount = 1
        elif self.tier == World.Tier.TIER_5:
            amount = 3
        elif self.tier == World.Tier.TIER_6:
            amount = 4
        elif self.tier == World.Tier.TIER_7:
            amount = 5

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

        return f"Lvl {amount} {protection_type}"

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

    def get_distance_to_world(self, world):
        distance_obj = WorldDistance.objects.filter(
            models.Q(world_1=self, world_2=world)
            | models.Q(world_1=world, world_2=self)
        ).first()

        if distance_obj is None:
            client = BoundlessClient()
            distance = client.get_world_distance(self.id, world.id)
            distance_obj = WorldDistance.objects.create(
                world_1=self, world_2=world, distance=int(distance)
            )

        return distance_obj.distance

    @cached_property
    def assignment_distance(self):
        if self.assignment is None:
            return None
        return self.get_distance_to_world(self.assignment)


class WorldDistance(models.Model):
    world_1 = models.ForeignKey(
        World, on_delete=models.CASCADE, related_name="+"
    )
    world_2 = models.ForeignKey(
        World, on_delete=models.CASCADE, related_name="+"
    )
    distance = models.PositiveSmallIntegerField(
        _("Distance to work in blinksecs")
    )


class WorldBlockColor(models.Model):
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    _new_color = models.NullBooleanField()
    _exist_on_perm = models.NullBooleanField()
    _exist_via_transform = models.NullBooleanField()

    class Meta:
        unique_together = ("world", "item")

    @property
    def exist_on_perm(self):
        if self._exist_on_perm is None:
            if self.world.start is None:
                exist_on_perm = True
            else:
                exist_on_perm = (
                    WorldBlockColor.objects.filter(
                        item=self.item,
                        color=self.color,
                        world__start__isnull=True,
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
            elif self.world.start is None:
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
                    world__start__isnull=True,
                ).count()
                > 0
            ):
                exist_via_transform = False

            exist_via_transform = (
                WorldBlockColor.objects.filter(
                    item__game_id__in=self.transform_group,
                    color=self.color,
                    world__start__isnull=True,
                ).count()
                > 0
            )

            self._exist_via_transform = exist_via_transform
            self.save()
        return self._exist_via_transform

    @cached_property
    def days_since_last(self):
        if self._new_color:
            return None

        # color exists on perm world
        if (
            WorldBlockColor.objects.filter(
                item=self.item, color=self.color, world__end__isnull=True
            ).count()
            > 0
        ):
            return None

        last = (
            WorldBlockColor.objects.filter(
                item=self.item,
                color=self.color,
                world__end__isnull=False,
                world__end__lt=self.world.start,
            )
            .order_by("-world__end")
            .first()
        )

        if last is None:
            return None

        return (self.world.start - last.world.end).days  # type: ignore


class WorldCreatureColor(models.Model):
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
            total_prestige=poll_dict["prestige"],
        )

        for index, amount in enumerate(poll_dict["resources"]):
            if amount == 0:
                continue

            item_id = settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING[index]

            item = Item.objects.get(game_id=item_id)

            ResourceCount.objects.create(
                world_poll=world_poll, item=item, count=amount
            )

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

        if new_world and world.is_exo:
            ExoworldNotification.objects.send_new_notification(world_poll)

        return world_poll


class WorldPoll(models.Model):
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


class WorldPollResult(models.Model):
    time = models.DateTimeField(auto_now=True, primary_key=True)
    world_poll = models.ForeignKey("WorldPoll", on_delete=models.CASCADE)
    player_count = models.PositiveSmallIntegerField(_("Player Count"))
    beacon_count = models.PositiveIntegerField(_("Beacon Count"))
    plot_count = models.PositiveIntegerField(_("Plot Count"))
    total_prestige = models.PositiveIntegerField(_("Total Prestige"))

    class Meta:
        unique_together = (
            "time",
            "world_poll",
        )


class ResourceCount(models.Model):
    time = models.DateTimeField(auto_now=True, primary_key=True)
    world_poll = models.ForeignKey("WorldPoll", on_delete=models.CASCADE)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(_("Count"))

    class Meta:
        unique_together = (
            "time",
            "world_poll",
            "item",
        )

        ordering = ["-count"]


class LeaderboardRecord(models.Model):
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


class ItemShopPriceManager(models.Manager):
    def create_from_shop_item(
        self, world: str, item: Item, shop_item: ShopItem
    ) -> ItemShopPrice:
        return self.create(
            item_id=item.id,
            beacon_name=shop_item.beacon_name,
            guild_tag=shop_item.guild_tag,
            item_count=shop_item.item_count,
            shop_activity=shop_item.shop_activity,
            price=shop_item.price,
            location_x=shop_item.location.x,
            location_y=shop_item.location.y,
            location_z=shop_item.location.z,
            world=World.objects.get(name=world),
        )


class ItemShopPrice(models.Model):
    time = models.DateTimeField(auto_now=True, primary_key=True)
    world = models.ForeignKey("World", on_delete=models.CASCADE)
    location_x = models.IntegerField()
    location_y = models.IntegerField()
    location_z = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    item_count = models.IntegerField()

    beacon_name = models.CharField(max_length=64, db_index=True)
    guild_tag = models.CharField(max_length=8)
    shop_activity = models.IntegerField()
    active = models.BooleanField(db_index=True, default=True)

    _location = None

    class Meta:
        abstract = True
        unique_together = (
            "time",
            "world",
            "location_x",
            "location_y",
            "item",
            "price",
            "item_count",
        )

    def __str__(self):
        return f"{self.item.default_name}: {self.item_count} @ {self.price}c"

    @property
    def location(self) -> Location:
        if self._location is None:
            self._location = Location(
                self.location_x, self.location_y, self.location_z
            )
        return self._location

    def refresh_from_db(self, using=None, fields=None):
        self._location = None
        return super().refresh_from_db(using, fields)

    @property
    def state_hash(self):
        return (
            f"{self.item.id}:{self.world.id}:{self.location_x}:"
            f"{self.location_y}:{self.location_z}:{self.price}:"
            f"{self.item_count}"
        ).encode("utf8")


class ItemShopStandPrice(ItemShopPrice):
    objects = ItemShopPriceManager()


class ItemRequestBasketPrice(ItemShopPrice):
    objects = ItemShopPriceManager()


class ItemRank(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(default=5)
    last_update = models.DateTimeField(blank=True, null=True)
    state_hash = models.CharField(max_length=128, default="")

    class Meta:
        abstract = True

    def __str__(self):
        return f"Rank: {self.rank} for {self.item} @ {self.world}"

    def increase_rank(self):
        if self.rank >= 20:
            self.rank = 10
        elif self.rank >= 10:
            self.rank = 5
        elif self.rank > 1:
            self.rank -= 1

    def decrease_rank(self):
        if self.rank < 30:
            self.rank += 1

    @property
    def query_delay(self):
        delay = settings.BOUNDLESS_BASE_ITEM_DELAY

        # decrease delay for more popular items
        # default: 30
        # popular (1-10) goes 10 * 6, 15, 20, 25, 30
        offset = settings.BOUNDLESS_INACTIVE_ITEM_DELAY_OFFSET
        if self.rank <= 10:
            offset = settings.BOUNDLESS_POPULAR_ITEM_DELAY_OFFSET
            delay = max(
                delay - offset * (10 - self.rank),
                settings.BOUNDLESS_MIN_ITEM_DELAY,
            )
        # inactive (11-19) goes 30, 40, 50, 60, 70, 80, 90, 100, 110, 120
        elif self.rank <= 20:
            delay = delay + offset * (self.rank - 11)
        # dead (20-30) goes 150, 180, 210, 240, 270, 300, 330, 360 * 3
        else:
            delay = min(
                delay
                + offset * (self.rank - 11)
                + offset * (self.rank - 20) * 2,
                settings.BOUNDLESS_MAX_ITEM_DELAY,
            )

        return delay

    @property
    def next_update(self):
        if self.last_update is None:
            return timezone.now() - timedelta(minutes=1)
        return self.last_update + timedelta(minutes=self.query_delay)


class ItemBuyRank(ItemRank):
    pass


class ItemSellRank(ItemRank):
    pass


@receiver(post_save)
def check_purge_cache(sender, **kwargs):
    # only purge for Boundless related models
    if "boundlexx.boundless.models" in repr(sender):
        purge_cache()
