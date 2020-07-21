from __future__ import annotations

from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from bge.boundless.client import Location, ShopItem


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
