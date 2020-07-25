from typing import Sequence, Type

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin

from boundlexx.boundless.models import (
    Color,
    Item,
    ItemBuyRank,
    ItemRequestBasketPrice,
    ItemSellRank,
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
        "time",
        "world",
        "location_x",
        "location_y",
        "location_z",
        "price",
        "item_count",
        "beacon_name",
        "guild_tag",
        "shop_activity",
    ]
    can_delete = False
    max_num = 0

    def get_queryset(self, request):
        return super().get_queryset(request).filter(active=True)


class ItemRankInline(admin.TabularInline):
    readonly_fields = [
        "world",
        "rank",
        "last_update",
        "state_hash",
        "next_update",
    ]
    can_delete = False
    max_num = 0


class ItemBuyRankInline(ItemRankInline):
    model = ItemBuyRank


class ItemSellRankInline(ItemRankInline):
    model = ItemSellRank


class ItemRequestBasketPriceInline(ItemPriceInline):
    model = ItemRequestBasketPrice


class ItemShopStandPriceInline(ItemPriceInline):
    model = ItemShopStandPrice


class GameObjAdmin(admin.ModelAdmin):
    list_display = ["default_name", "game_id", "active"]
    search_fields = ["game_id", "localizedname"]
    readonly_fields = ["game_id"]

    inlines: Sequence[Type[InlineModelAdmin]] = [LocalizationInline]

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
    readonly_fields = ["game_id", "string_id"]
    raw_id_fields = ["item_subtitle"]
    inlines = [
        LocalizationInline,
        ItemBuyRankInline,
        ItemRequestBasketPriceInline,
        ItemSellRankInline,
        ItemShopStandPriceInline,
    ]


class ItemPriceAdmin(admin.ModelAdmin):
    raw_id_fields = ["item"]
    list_display = [
        "item",
        "item_count",
        "world",
        "location",
        "price",
        "beacon_name",
        "active",
    ]
    readonly_fields = [
        "time",
        "world",
        "location_x",
        "location_y",
        "location_z",
        "price",
        "item_count",
        "beacon_name",
        "guild_tag",
        "shop_activity",
    ]
    search_fields = ["item__default_name", "world", "beacon_name"]


@admin.register(ItemRequestBasketPrice)
class ItemRequestBasketPriceAdmin(ItemPriceAdmin):
    pass


@admin.register(ItemShopStandPrice)
class ItemShopStandPriceAdmin(ItemPriceAdmin):
    pass
