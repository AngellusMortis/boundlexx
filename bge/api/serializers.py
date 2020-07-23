from rest_framework import serializers

from bge.boundless.models import Color, Item, LocalizedName


class LocalizedNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalizedName
        fields = ["lang", "name"]


class ColorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="game_id")  # noqa A003
    localization = LocalizedNameSerializer(
        source="localizedname_set", many=True
    )

    class Meta:
        model = Color
        fields = ["id", "localization"]


class ItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="game_id")  # noqa A003
    localization = LocalizedNameSerializer(
        source="localizedname_set", many=True
    )

    class Meta:
        model = Item
        fields = ["id", "string_id", "localization"]
