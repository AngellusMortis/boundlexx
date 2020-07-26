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
    LeaderboardRecord,
    LocalizedName,
    Metal,
    ResourceCount,
    Subtitle,
    World,
    WorldPoll,
    WorldPollResult,
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


class WorldPollInline(admin.TabularInline):
    model = WorldPoll

    show_change_link = True
    fields = ["active", "time"]
    readonly_fields = ["time"]
    can_delete = False
    max_num = 0


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    list_display = ["display_name", "region", "tier", "world_type", "is_perm"]
    fields = [
        "active",
        "name",
        "display_name",
        "region",
        "tier",
        "description",
        "size",
        "world_type",
        "address",
        "ip_address",
        "api_url",
        "planets_url",
        "chunks_url",
        "time_offset",
        "websocket_url",
        "atmosphere_color",
        "water_color",
        "start",
        "end",
    ]
    readonly_fields = [
        "name",
        "display_name",
        "region",
        "tier",
        "description",
        "size",
        "world_type",
        "address",
        "ip_address",
        "api_url",
        "planets_url",
        "chunks_url",
        "time_offset",
        "websocket_url",
        "atmosphere_color",
        "water_color",
        "start",
        "end",
    ]

    inlines = [WorldPollInline]


class WorldPollResultInline(admin.StackedInline):
    model = WorldPollResult

    readonly_fields = [
        "player_count",
        "beacon_count",
        "plot_count",
        "total_prestige",
    ]
    can_delete = False
    max_num = 0


class ResourceCountInline(admin.TabularInline):
    model = ResourceCount

    fields = [
        "item",
        "count",
    ]
    readonly_fields = [
        "item",
        "count",
    ]
    can_delete = False
    max_num = 0


class LeaderboardRecordInline(admin.TabularInline):
    model = LeaderboardRecord

    fields = [
        "world_rank",
        "guild_tag",
        "mayor_name",
        "name",
        "prestige",
    ]
    readonly_fields = [
        "world_rank",
        "guild_tag",
        "mayor_name",
        "name",
        "prestige",
    ]
    can_delete = False
    max_num = 0


@admin.register(WorldPoll)
class WorldPollAdmin(admin.ModelAdmin):
    list_display = ["world", "time", "active"]

    fields = ["active", "world", "time"]
    readonly_fields = ["time"]

    inlines = [
        WorldPollResultInline,
        LeaderboardRecordInline,
        ResourceCountInline,
    ]
