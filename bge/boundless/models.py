from __future__ import annotations

from django.db import models
from django.utils import timezone

from bge.boundless.client import Location, ShopItem


class Item(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    gui_name = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return self.gui_name

    @property
    def buy_locations(self):
        return self.itemshopstandprice_set.filter(active=True)

    @property
    def sell_locations(self):
        return self.itemrequestbasketprice_set.filter(active=True)


class ItemShopPrice(models.Model):
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    beacon_name = models.CharField(max_length=64, db_index=True)
    guild_tag = models.CharField(max_length=8)
    world = models.CharField(max_length=64, db_index=True)
    item_count = models.IntegerField()
    shop_activity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location_x = models.IntegerField()
    location_y = models.IntegerField()
    location_z = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    active = models.BooleanField(db_index=True, default=True)

    _location = None

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.item.gui_name}: {self.item_count} @ {self.price}c"

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
        obj, created = manager.get_or_create(
            item_id=item.id,
            beacon_name=shop_item.beacon_name,
            guild_tag=shop_item.guild_tag,
            item_count=shop_item.item_count,
            shop_activity=shop_item.shop_activity,
            price=shop_item.price,
            location_x=shop_item.location.x,
            location_y=shop_item.location.y,
            location_z=shop_item.location.z,
            world=world,
        )

        if not created:
            obj.active = True
            obj.last_updated = timezone.now()
            obj.save()

        return obj


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
