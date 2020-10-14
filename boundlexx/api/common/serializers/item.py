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

    class Meta:
        model = Item
        fields = [
            "game_id",
            "name",
            "string_id",
            "localization",
            "item_subtitle",
            "list_type",
        ]


class ItemSerializer(SimpleItemSerializer):
    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    description = LocalizedStringSerializer()

    mint_value = serializers.FloatField()

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
            "list_type",
            "description",
        ]


class ItemResourceCountSerializer(serializers.ModelSerializer):
    world = IDWorldSerializer(source="world_poll.world")

    class Meta:
        model = ResourceCount
        fields = [
            "world",
            "is_embedded",
            "percentage",
            "count",
            "average_per_chunk",
        ]