from rest_framework import serializers

from boundlexx.api.common.serializers.base import (
    LocalizedNameSerializer,
    LocalizedStringSerializer,
)
from boundlexx.boundless.models import Item, Subtitle


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

    class Meta:
        model = Item
        fields = [
            "game_id",
            "name",
            "string_id",
            "localization",
            "item_subtitle",
        ]


class ItemSerializer(SimpleItemSerializer):
    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    list_type = LocalizedStringSerializer()
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
