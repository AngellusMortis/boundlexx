from rest_framework import serializers

from bge.boundless.models import Color, LocalizedName


class LocalizedNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalizedName
        fields = ["lang", "name"]


class ColorSerializer(serializers.ModelSerializer):
    localization = LocalizedNameSerializer(
        source="localizedname_set", many=True
    )

    class Meta:
        model = Color
        fields = ["game_id", "default_name", "localization"]
