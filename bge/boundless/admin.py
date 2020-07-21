from django.contrib import admin
from typing import List

from bge.boundless.models import (
    Color,
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    LocalizedName,
    Metal,
    Subtitle,
)


class LocalizationInline(admin.TabularInline):
    model = LocalizedName
    readonly_fields = [
        "lang",
        "name",
    ]
    can_delete = False
    max_num = 0


class ItemPriceInline(admin.TabularInline):
    fk_name = "item"
    readonly_fields = [
        "beacon_name",
        "guild_tag",
        "world",
        "shop_activity",
        "location_x",
        "location_y",
        "location_z",
        "last_updated",
        "item_count",
        "price",
        "world",
    ]
    can_delete = False
    max_num = 0

    def get_queryset(self, request):
        return super().get_queryset(request).filter(active=True)


class ItemRequestBasketPriceInline(ItemPriceInline):
    model = ItemRequestBasketPrice


class ItemShopStandPriceInline(ItemPriceInline):
    model = ItemShopStandPrice


class GameObjAdmin(admin.ModelAdmin):
    list_display = ["default_name", "game_id", "active"]
    search_fields = ["game_id", "localizedname"]
    readonly_fields = ["game_id"]

    inlines = [LocalizationInline]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Subtitle)
class SubtitleAdmin(GameObjAdmin):
    pass


@admin.register(Color)
class ColorAdmin(GameObjAdmin):
    pass


@admin.register(Metal)
class MetalAdmin(GameObjAdmin):
    pass


@admin.register(Item)
class ItemAdmin(GameObjAdmin):
    raw_id_fields = ["item_subtitle"]
    inlines: List[admin.ModelAdmin] = [
        ItemRequestBasketPriceInline,
        ItemShopStandPriceInline,
    ]


class ItemPriceAdmin(admin.ModelAdmin):
    raw_id_fields = ["item"]
    list_display = [
        "item",
        "item_count",
        "price",
        "world",
        "beacon_name",
        "location",
        "active",
    ]
    readonly_fields = [
        "beacon_name",
        "guild_tag",
        "world",
        "shop_activity",
        "location_x",
        "location_y",
        "location_z",
        "last_updated",
        "item_count",
        "price",
        "world",
    ]
    search_fields = ["item__default_name", "world", "beacon_name"]


@admin.register(ItemRequestBasketPrice)
class ItemRequestBasketPriceAdmin(ItemPriceAdmin):
    pass


@admin.register(ItemShopStandPrice)
class ItemShopStandPriceAdmin(ItemPriceAdmin):
    pass
