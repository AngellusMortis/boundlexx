from __future__ import annotations

from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from boundlexx.boundless.client import Location, ShopItem
from boundlexx.boundless.utils import convert_linear_rgb_to_hex


class GameObjManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("localizedname")


class GameObj(PolymorphicModel):
    active = models.BooleanField(_("Active"), default=True)
    game_id = models.IntegerField(_("Game ID"), db_index=True)

    class Meta:
        unique_together = ("game_id", "polymorphic_ctype")

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
    name = models.CharField(_("Name"), max_length=128)

    class Meta:
        unique_together = ("game_obj", "lang")

    def __str__(self):
        return f"{self.lang}: {self.name}"


class Subtitle(GameObj):
    pass


class Color(GameObj):
    pass


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
    def buy_locations(self):
        return self.itemshopstandprice_set.filter(active=True)

    @property
    def sell_locations(self):
        return self.itemrequestbasketprice_set.filter(active=True)


class World(models.Model):
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

    name = models.CharField(_("Name"), max_length=64)
    display_name = models.CharField(_("Display Name"), max_length=64)
    region = models.CharField(
        _("Server Region"), max_length=16, choices=Region.choices
    )
    tier = models.PositiveSmallIntegerField(_("Tier"), choices=Tier.choices)
    description = models.CharField(_("Description"), max_length=32)
    size = models.IntegerField(_("World Size"))
    world_type = models.CharField(
        _("World Type"), choices=WorldType.choices, max_length=9
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
    time_offset = models.DateTimeField(_("Time Offset"))
    websocket_url = models.URLField(_("Websocket URL"), blank=True, null=True)
    assignment = models.PositiveSmallIntegerField(blank=True, null=True)
    owner = models.PositiveSmallIntegerField(blank=True, null=True)
    creative = models.BooleanField(default=False, db_index=True)
    locked = models.BooleanField(default=False, db_index=True)
    public = models.BooleanField(default=True, db_index=True)
    number_of_regions = models.PositiveSmallIntegerField(blank=True, null=True)

    atmosphere_color_r = models.FloatField(_("Atmosphere Linear R Color"))
    atmosphere_color_g = models.FloatField(_("Atmosphere Linear G Color"))
    atmosphere_color_b = models.FloatField(_("Atmosphere Linear B Color"))
    water_color_r = models.FloatField(_("Water Linear R Color"))
    water_color_g = models.FloatField(_("Water Linear G Color"))
    water_color_b = models.FloatField(_("Water Linear B Color"))

    active = models.BooleanField(default=True, db_index=True)

    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.display_name

    @staticmethod
    def from_world_dict(world_dict):
        created = False
        try:
            world = World.objects.get(id=world_dict["id"])
        except World.DoesNotExist:
            world = World.objects.create(
                id=world_dict["id"],
                name=world_dict["name"],
                display_name=world_dict["displayName"],
                region=world_dict["region"],
                tier=world_dict["tier"],
                description=world_dict["worldDescription"],
                size=world_dict["worldSize"],
                world_type=world_dict["worldType"],
                time_offset=datetime.utcfromtimestamp(
                    world_dict["timeOffset"]
                ).replace(tzinfo=pytz.utc),
                atmosphere_color_r=world_dict["atmosphereColor"][0],
                atmosphere_color_g=world_dict["atmosphereColor"][1],
                atmosphere_color_b=world_dict["atmosphereColor"][2],
                water_color_r=world_dict["waterColor"][0],
                water_color_g=world_dict["waterColor"][1],
                water_color_b=world_dict["waterColor"][2],
            )
            created = True

        world.address = world_dict.get("addr")
        world.ip_address = world_dict.get("ipAddr")
        world.api_url = world_dict.get("apiURL")
        world.websocket_url = world_dict.get("websocketURL")
        world.creative = world_dict.get("creative", False)
        world.owner = world_dict.get("owner", None)
        world.assignment = world_dict.get("assignment", None)
        world.locked = world_dict.get("locked", False)
        world.number_of_regions = world_dict["numRegions"]

        if "lifetime" in world_dict:
            world.start = datetime.utcfromtimestamp(
                world_dict["lifetime"][0]
            ).replace(tzinfo=pytz.utc)
            world.end = datetime.utcfromtimestamp(
                world_dict["lifetime"][1]
            ).replace(tzinfo=pytz.utc)
        world.save()

        return world, created

    @property
    def is_perm(self):
        return self.end is None

    @property
    def atmosphere_color(self):
        return convert_linear_rgb_to_hex(
            self.atmosphere_color_r,
            self.atmosphere_color_g,
            self.atmosphere_color_b,
        )

    @property
    def water_color(self):
        return convert_linear_rgb_to_hex(
            self.water_color_r, self.water_color_g, self.water_color_b,
        )

    @property
    def protection(self):
        if self.tier < World.Tier.TIER_4:
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


class WorldPoll(models.Model):
    world = models.ForeignKey("World", on_delete=models.CASCADE)
    active = models.BooleanField(db_index=True, default=True)
    time = models.DateTimeField(auto_now=True)

    @property
    def result(self):
        return self.worldpollresult_set.first()

    @property
    def resources(self):
        return self.resourcecount_set.all()

    @property
    def leaderboard(self):
        return self.leaderboardrecord_set.all()

    @staticmethod
    def from_world_poll_dict(world_dict, poll_dict, world=None):
        if world is None:
            world, _ = World.from_world_dict(world_dict)

        world_poll = WorldPoll.objects.create(world=world)

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

        return world_poll


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


class LeaderboardRecord(models.Model):
    time = models.DateTimeField(auto_now=True, primary_key=True)
    world_poll = models.ForeignKey("WorldPoll", on_delete=models.CASCADE)
    world_rank = models.PositiveSmallIntegerField(_("World Rank"))
    guild_tag = models.CharField(_("Guild Tag"), max_length=7)
    mayor_id = models.PositiveSmallIntegerField()
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

    @staticmethod
    def from_shop_item(
        manager, world: str, item: Item, shop_item: ShopItem
    ) -> ItemShopPrice:
        return manager.create(
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

    @property
    def state_hash(self):
        return (
            f"{self.item.id}:{self.world.id}:{self.location_x}:"
            f"{self.location_y}:{self.location_z}:{self.price}:"
            f"{self.item_count}"
        ).encode("utf8")


class ItemShopStandPrice(ItemShopPrice):
    @staticmethod
    def from_shop_item(  # type: ignore # pylint: disable=arguments-differ
        world: str, item: Item, shop_item: ShopItem
    ) -> ItemShopPrice:
        return ItemShopPrice.from_shop_item(
            ItemShopStandPrice.objects, world, item, shop_item
        )


class ItemRequestBasketPrice(ItemShopPrice):
    @staticmethod
    def from_shop_item(  # type: ignore # pylint: disable=arguments-differ
        world: str, item: Item, shop_item: ShopItem
    ) -> ItemShopPrice:
        return ItemShopPrice.from_shop_item(
            ItemRequestBasketPrice.objects, world, item, shop_item
        )


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