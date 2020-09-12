from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

from boundlexx.boundless.client import Location, ShopItem
from boundlexx.boundless.models.game import Item
from boundlexx.boundless.models.world import World


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
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    location_x = models.IntegerField()
    location_y = models.IntegerField()
    location_z = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
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
            self._location = Location(self.location_x, self.location_y, self.location_z)
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


class ItemShopStandPrice(
    ExportModelOperationsMixin("item_shop_stand_price"), ItemShopPrice  # type: ignore  # noqa E501
):
    objects = ItemShopPriceManager()


class ItemRequestBasketPrice(
    ExportModelOperationsMixin("item_request_basket_price"), ItemShopPrice  # type: ignore  # noqa E501
):
    objects = ItemShopPriceManager()


class ItemRank(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(default=20)
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
                delay + offset * (self.rank - 11) + offset * (self.rank - 20) * 2,
                settings.BOUNDLESS_MAX_ITEM_DELAY,
            )

        return delay

    @property
    def next_update(self):
        if self.last_update is None:
            return timezone.now() - timedelta(minutes=1)
        return self.last_update + timedelta(minutes=self.query_delay)


class ItemBuyRank(ExportModelOperationsMixin("item_buy_rank"), ItemRank):  # type: ignore  # noqa E501
    pass


class ItemSellRank(ExportModelOperationsMixin("item_sell_rank"), ItemRank):  # type: ignore  # noqa E501
    pass
