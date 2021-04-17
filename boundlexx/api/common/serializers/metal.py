from rest_framework import serializers

from boundlexx.api.common.serializers.base import LocalizedNameSerializer
from boundlexx.boundless.models import Metal


class IDMetalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metal
        fields = [
            "game_id",
        ]


class MetalSerializer(serializers.ModelSerializer):
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )

    class Meta:
        model = Metal
        fields = [
            "game_id",
            "localization",
        ]
