from django.conf import settings
from rest_framework import serializers
from rest_framework.relations import Hyperlink
from rest_framework.reverse import reverse

from boundlexx.boundless.models import (
    Color,
    Item,
    LocalizedName,
    ResourceCount,
    World,
)


class ResourceCountLinkField(serializers.ModelField):
    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["model_field"] = None
        super().__init__(*args, **kwargs)

    def to_representation(self, value):  # pylint: disable=arguments-differ
        return Hyperlink(value, None)

    def get_attribute(self, obj):
        if obj.game_id in settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING:
            return reverse(
                "item-resource-count-list",
                kwargs={"item__game_id": obj.game_id},
                request=self.context["request"],
            )
        return None


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
    resource_counts = ResourceCountLinkField()

    class Meta:
        model = Item
        fields = ["id", "string_id", "resource_counts", "localization"]


class SimpleWorldSerializer(serializers.ModelSerializer):
    class Meta:
        model = World
        fields = ["id", "display_name"]


class ItemResourceCountSerializer(serializers.ModelSerializer):
    world = SimpleWorldSerializer(source="world_poll.world")

    class Meta:
        model = ResourceCount
        fields = ["world", "count"]
