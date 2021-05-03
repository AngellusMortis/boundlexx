from typing import Optional

from rest_framework import serializers

from boundlexx.api.models import ExportedFile
from boundlexx.boundless.models import (
    LocalizedName,
    LocalizedString,
    LocalizedStringText,
    World,
)

BASE_QUERY = World.objects.all().select_related("assignment")


class NullSerializer(serializers.Serializer):
    def create(self, validated_data):
        return

    def update(self, instance, validated_data):
        return


class WorldIDPostSerializer(NullSerializer):
    world_id = serializers.IntegerField(
        required=True,
        help_text=(
            "World ID of given world. You can get "
            'your World ID from the <a href="https://forum.playboundless.com/'
            "uploads/default/original/3X/3/f/3fef2e21cedc3d4594971d6143d40110bd489686"
            '.jpeg" target="_blank">Debug Menu</a> if you are on PC'
        ),
        label="World ID",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world: Optional[World] = None

    def validate_world_id(self, value):
        try:
            world = BASE_QUERY.get(pk=value)
        except World.DoesNotExist:
            raise serializers.ValidationError(  # pylint: disable=raise-missing-from
                "Could not find a world with that ID"
            )
        else:
            self.world = world

        return value


class AzureImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None

        try:
            url = value.url
        except AttributeError:
            return None

        return url


class LangFilterListSerializer(
    serializers.ListSerializer
):  # pylint: disable=abstract-method
    def to_representation(self, data):
        data = super().to_representation(data)
        lang = self.context["request"].query_params.get("lang", "all")

        if lang == "all":
            return data
        if lang == "none":
            return []

        new_data = []
        for item in data:
            if item["lang"] == lang:
                new_data.append(item)
        data = new_data

        return data


class LocalizedStringTextSerializer(serializers.ModelSerializer):
    plain_text = serializers.CharField()

    class Meta:
        model = LocalizedStringText
        list_serializer_class = LangFilterListSerializer
        fields = ["lang", "text", "plain_text"]


class LocalizedStringSerializer(serializers.ModelSerializer):
    strings = LocalizedStringTextSerializer(many=True)

    class Meta:
        model = LocalizedString
        list_serializer_class = LangFilterListSerializer
        fields = ["string_id", "strings"]


class LocalizedNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalizedName
        list_serializer_class = LangFilterListSerializer
        fields = ["lang", "name"]


class LocationSerializer(NullSerializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    z = serializers.IntegerField()

    def to_representation(self, instance):
        return {
            "x": instance.x,
            "y": instance.y,
            "z": instance.z,
        }


class ExportedFileSerializer(serializers.ModelSerializer):
    url = AzureImageField(source="exported_file")

    class Meta:
        model = ExportedFile
        fields = ["name", "description", "url"]
