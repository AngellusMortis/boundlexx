from django.conf import settings
from rest_framework import serializers
from rest_framework.relations import Hyperlink
from rest_framework.reverse import reverse

from boundlexx.boundless.models import (
    Color,
    Item,
    LeaderboardRecord,
    LocalizedName,
    ResourceCount,
    World,
    WorldPoll,
)


class NestedHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def get_url(
        self,
        obj,
        view_name,
        request,
        format,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None

        kwargs = {}
        for index, lookup_field in enumerate(self.lookup_field):
            attrs = lookup_field.split(".")

            lookup_value = obj
            for attr in attrs:
                lookup_value = getattr(lookup_value, attr)

            kwargs[self.lookup_url_kwarg[index]] = lookup_value

        return self.reverse(
            view_name, kwargs=kwargs, request=request, format=format
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


class LangFilterListSerializer(
    serializers.ListSerializer
):  # pylint: disable=abstract-method
    def to_representation(self, data):
        data = super().to_representation(data)

        if "lang" in self.context["request"].query_params:
            lang = self.context["request"].query_params["lang"]
            new_data = []
            for item in data:
                if item["lang"] == lang:
                    new_data.append(item)
            data = new_data

        return data


class LocalizedNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalizedName
        list_serializer_class = LangFilterListSerializer
        fields = ["lang", "name"]


class ColorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="color-detail", lookup_field="game_id", read_only=True
    )
    localization = LocalizedNameSerializer(
        source="localizedname_set", many=True
    )

    class Meta:
        model = Color
        fields = ["url", "game_id", "localization"]


class ItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="item-detail", lookup_field="game_id", read_only=True
    )
    resource_counts_url = ResourceCountLinkField()
    localization = LocalizedNameSerializer(
        source="localizedname_set", many=True
    )

    class Meta:
        model = Item
        fields = [
            "url",
            "game_id",
            "string_id",
            "resource_counts_url",
            "localization",
        ]


class SimpleWorldSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="world-detail", lookup_field="id", read_only=True
    )

    class Meta:
        model = World
        fields = ["url", "id", "display_name"]


class ItemResourceCountSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name="item-resource-count-detail",
        lookup_field=["item.game_id", "world_poll.world.id"],
        lookup_url_kwarg=["item__game_id", "world_id"],
        read_only=True,
    )
    item_url = NestedHyperlinkedIdentityField(
        view_name="item-detail",
        lookup_field=["item.game_id"],
        lookup_url_kwarg=["game_id"],
        read_only=True,
    )
    world = SimpleWorldSerializer(source="world_poll.world")

    class Meta:
        model = ResourceCount
        fields = ["url", "item_url", "world", "count"]


class WorldSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="world-detail", lookup_field="id", read_only=True
    )
    polls_url = NestedHyperlinkedIdentityField(
        view_name="world-poll-list",
        lookup_field=["id"],
        lookup_url_kwarg=["world_id"],
        read_only=True,
    )

    class Meta:
        model = World
        fields = [
            "url",
            "polls_url",
            "id",
            "name",
            "display_name",
            "region",
            "tier",
            "description",
            "size",
            "world_type",
            "time_offset",
            "is_sovereign",
            "is_perm",
            "is_creative",
            "is_locked",
            "is_public",
            "number_of_regions",
            "start",
            "end",
            "atmosphere_color",
            "water_color",
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderboardRecord
        fields = ["world_rank", "guild_tag", "mayor_name", "name", "prestige"]


class SimpleItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="item-detail", lookup_field="game_id", read_only=True
    )

    class Meta:
        model = Item
        fields = [
            "url",
            "game_id",
            "string_id",
        ]


class ResourcesSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()

    class Meta:
        model = ResourceCount
        fields = ["item", "count"]


class WorldPollSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name="world-poll-detail",
        lookup_field=["world.id", "id"],
        lookup_url_kwarg=["world_id", "id"],
        read_only=True,
    )
    world = SimpleWorldSerializer()

    player_count = serializers.IntegerField(
        source="result.player_count", read_only=True
    )
    beacon_count = serializers.IntegerField(
        source="result.beacon_count", read_only=True
    )
    plot_count = serializers.IntegerField(
        source="result.plot_count", read_only=True
    )
    total_prestige = serializers.IntegerField(
        source="result.total_prestige", read_only=True
    )
    leaderboard = LeaderboardSerializer(
        many=True, source="leaderboardrecord_set"
    )
    resources = ResourcesSerializer(many=True, source="resourcecount_set")

    class Meta:
        model = WorldPoll
        fields = [
            "url",
            "id",
            "time",
            "world",
            "player_count",
            "beacon_count",
            "plot_count",
            "total_prestige",
            "leaderboard",
            "resources",
        ]
