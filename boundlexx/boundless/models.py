from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from boundlexx.boundless.client import Location, ShopItem


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
    REGION_USE = "use"
    REGION_USW = "usw"
    REGION_EUC = "ecu"
    REGION_AUS = "aus"
    REGION_CREATIVE = "creative"

    REGION_CHOICES = [
        (REGION_USE, "US East"),
        (REGION_USE, "US West"),
        (REGION_EUC, "EU Central"),
        (REGION_AUS, "Australia"),
        (REGION_CREATIVE, "Creative"),
    ]

    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64)
    region = models.CharField(max_length=16, choices=REGION_CHOICES)
    tier = models.IntegerField()
    description = models.CharField(max_length=16)
    size = models.IntegerField()
    world_type = models.CharField(max_length=16)

    active = models.BooleanField(default=True, db_index=True)
    is_perm = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return self.display_name


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
