from django.contrib import admin

from bge.boundless.models import (
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("gui_name", "id", "name", "active")
    search_fields = ("id", "name", "gui_name")


@admin.register(ItemRequestBasketPrice)
class ItemRequestBasketPriceAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "item_count",
        "price",
        "world",
        "beacon_name",
        "location",
        "active",
    )
    search_fields = ("item__guiname", "world", "beacon_name")


@admin.register(ItemShopStandPrice)
class ItemShopStandPriceAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "item_count",
        "price",
        "world",
        "beacon_name",
        "location",
        "active",
    )
    search_fields = ("item__guiname", "world", "beacon_name")
