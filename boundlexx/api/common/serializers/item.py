from rest_framework import serializers

from boundlexx.api.common.serializers.base import (
    LocalizedNameSerializer,
    LocalizedStringSerializer,
)
from boundlexx.api.common.serializers.world import IDWorldSerializer
from boundlexx.boundless.models import Item, ResourceCount, Subtitle


class SubtitleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # noqa: A003
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )

    class Meta:
        model = Subtitle
        fields = ["id", "localization"]


class IDItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "game_id",
        ]


class SimpleItemSerializer(IDItemSerializer):
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )

    item_subtitle = SubtitleSerializer()
    list_type = LocalizedStringSerializer()
    has_colors = serializers.BooleanField()
    is_resource = serializers.BooleanField()

    class Meta:
        model = Item
        fields = [
            "game_id",
            "name",
            "string_id",
            "localization",
            "item_subtitle",
            "list_type",
            "has_colors",
            "is_resource",
        ]


class ItemSerializer(SimpleItemSerializer):
    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    description = LocalizedStringSerializer()

    mint_value = serializers.FloatField()
    max_stack = serializers.IntegerField()

    class Meta:
        model = Item
        fields = [
            "game_id",
            "name",
            "string_id",
            "next_request_basket_update",
            "next_shop_stand_update",
            "localization",
            "item_subtitle",
            "mint_value",
            "max_stack",
            "list_type",
            "description",
            "has_colors",
            "is_resource",
        ]


class ItemResourceCountSerializer(serializers.ModelSerializer):
    world = IDWorldSerializer(source="world_poll.world")
    average_per_chunk = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = ResourceCount
        fields = [
            "world",
            "is_embedded",
            "percentage",
            "count",
            "average_per_chunk",
        ]
