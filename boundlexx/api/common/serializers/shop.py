from rest_framework import serializers

from boundlexx.api.common.serializers.base import LocationSerializer
from boundlexx.api.common.serializers.item import IDItemSerializer
from boundlexx.api.common.serializers.world import IDWorldSerializer
from boundlexx.boundless.models import ItemRequestBasketPrice, ItemShopStandPrice


class BaseItemShopSerializer(serializers.ModelSerializer):
    world = IDWorldSerializer()
    item = IDItemSerializer()
    location = LocationSerializer()
    time = serializers.DateTimeField()


class WorldShopStandPriceSerializer(BaseItemShopSerializer):
    class Meta:
        model = ItemShopStandPrice
        fields = [
            "time",
            "location",
            "item",
            "item_count",
            "price",
            "beacon_name",
            "guild_tag",
            "shop_activity",
        ]


class WorldRequestBasketPriceSerializer(BaseItemShopSerializer):
    class Meta:
        model = ItemRequestBasketPrice
        fields = [
            "time",
            "location",
            "item",
            "item_count",
            "price",
            "beacon_name",
            "guild_tag",
            "shop_activity",
        ]


class ItemShopStandPriceSerializer(BaseItemShopSerializer):
    class Meta:
        model = ItemShopStandPrice
        fields = [
            "time",
            "location",
            "world",
            "item_count",
            "price",
            "beacon_name",
            "guild_tag",
            "shop_activity",
        ]


class ItemRequestBasketPriceSerializer(BaseItemShopSerializer):
    class Meta:
        model = ItemRequestBasketPrice
        fields = [
            "time",
            "location",
            "world",
            "item_count",
            "price",
            "beacon_name",
            "guild_tag",
            "shop_activity",
        ]
