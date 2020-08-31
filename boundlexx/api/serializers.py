from rest_framework import serializers
from rest_framework.relations import Hyperlink
from rest_framework.reverse import reverse

from boundlexx.boundless.models import (
    Color,
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    LeaderboardRecord,
    LocalizedName,
    ResourceCount,
    Subtitle,
    World,
    WorldBlockColor,
    WorldDistance,
    WorldPoll,
)


class AzureImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None

        try:
            url = value.url
        except AttributeError:
            return None

        return url


class LocationSerializer(serializers.DictField):
    def to_representation(self, value):
        return {
            "x": value.x,
            "y": value.y,
            "z": value.z,
        }


class NullSerializer(serializers.Serializer):
    def create(self, validated_data):
        return

    def update(self, instance, validated_data):
        return


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


class ActiveWorldUrlHyperlinkField(serializers.HyperlinkedIdentityField):
    def get_url(
        self,
        obj,
        view_name,
        request,
        format,  # pylint: disable=redefined-builtin  # noqa A002
    ):
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None

        if not obj.active:
            return None

        return super().get_url(obj, view_name, request, format)


class ResourceCountLinkField(serializers.ModelField):
    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["model_field"] = None
        kwargs["allow_null"] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):  # pylint: disable=arguments-differ
        return Hyperlink(value, None)

    def get_attribute(self, obj):
        if obj.is_resource:
            return reverse(
                "item-resource-count-list",
                kwargs={"item__game_id": obj.game_id},
                request=self.context["request"],
            )
        return None


class ItemColorsLinkField(serializers.ModelField):
    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["model_field"] = None
        kwargs["allow_null"] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):  # pylint: disable=arguments-differ
        return Hyperlink(value, None)

    def get_attribute(self, obj):
        if obj.has_colors:
            return reverse(
                "item-colors-list",
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
        view_name="color-detail",
        lookup_field="game_id",
        read_only=True,
    )
    blocks_url = serializers.HyperlinkedIdentityField(
        view_name="color-blocks-list",
        lookup_field="game_id",
        lookup_url_kwarg="color__game_id",
        read_only=True,
    )
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )

    class Meta:
        model = Color
        fields = [
            "url",
            "blocks_url",
            "game_id",
            "base_color",
            "gleam_color",
            "localization",
        ]


class SubtitleSerializer(serializers.ModelSerializer):
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )

    class Meta:
        model = Subtitle
        fields = ["localization"]


class ItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="item-detail",
        lookup_field="game_id",
        read_only=True,
    )
    resource_counts_url = ResourceCountLinkField()
    request_baskets_url = serializers.HyperlinkedIdentityField(
        view_name="item-shop-stands",
        lookup_field="game_id",
        read_only=True,
    )
    shop_stands_url = serializers.HyperlinkedIdentityField(
        view_name="item-request-baskets",
        lookup_field="game_id",
        read_only=True,
    )
    colors_url = ItemColorsLinkField()
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )
    item_subtitle = SubtitleSerializer()

    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    class Meta:
        model = Item
        fields = [
            "url",
            "colors_url",
            "game_id",
            "string_id",
            "resource_counts_url",
            "request_baskets_url",
            "next_request_basket_update",
            "shop_stands_url",
            "next_shop_stand_update",
            "localization",
            "item_subtitle",
        ]


class SimpleWorldSerializer(serializers.ModelSerializer):
    url = ActiveWorldUrlHyperlinkField(
        view_name="world-detail",
        lookup_field="id",
        read_only=True,
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
        fields = [
            "url",
            "item_url",
            "world",
            "is_embedded",
            "percentage",
            "count",
        ]


class ItemResourceCountTimeSeriesSerializer(ItemResourceCountSerializer):
    class Meta:
        model = ResourceCount
        fields = [
            "time",
            "url",
            "item_url",
            "world",
            "is_embedded",
            "percentage",
            "count",
        ]


class WorldSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="world-detail",
        lookup_field="id",
        read_only=True,
    )
    polls_url = NestedHyperlinkedIdentityField(
        view_name="world-poll-list",
        lookup_field=["id"],
        lookup_url_kwarg=["world_id"],
        read_only=True,
    )
    block_colors_url = serializers.HyperlinkedIdentityField(
        view_name="world-block-colors",
        lookup_field="id",
        read_only=True,
    )
    distances_url = NestedHyperlinkedIdentityField(
        view_name="world-distance-list",
        lookup_field=["id"],
        lookup_url_kwarg=["world_source__id"],
        read_only=True,
    )
    request_baskets_url = serializers.HyperlinkedIdentityField(
        view_name="world-shop-stands",
        lookup_field="id",
        read_only=True,
    )
    shop_stands_url = serializers.HyperlinkedIdentityField(
        view_name="world-request-baskets",
        lookup_field="id",
        read_only=True,
    )
    assignment = SimpleWorldSerializer()
    image_url = AzureImageField(source="image", allow_null=True)
    forum_url = serializers.URLField(allow_null=True)

    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    class Meta:
        model = World
        fields = [
            "url",
            "polls_url",
            "block_colors_url",
            "distances_url",
            "request_baskets_url",
            "next_request_basket_update",
            "shop_stands_url",
            "next_shop_stand_update",
            "id",
            "name",
            "display_name",
            "image_url",
            "forum_url",
            "assignment",
            "region",
            "tier",
            "description",
            "size",
            "world_type",
            "time_offset",
            "is_sovereign",
            "is_perm",
            "is_exo",
            "is_creative",
            "is_locked",
            "is_public",
            "number_of_regions",
            "start",
            "end",
            "atmosphere_color",
            "water_color",
            "surface_liquid",
            "core_liquid",
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderboardRecord
        fields = ["world_rank", "guild_tag", "mayor_name", "name", "prestige"]


class SimpleItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="item-detail",
        lookup_field="game_id",
        read_only=True,
    )

    class Meta:
        model = Item
        fields = [
            "url",
            "game_id",
            "string_id",
        ]


class SimpleColorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="color-detail",
        lookup_field="game_id",
        read_only=True,
    )

    class Meta:
        model = Item
        fields = [
            "url",
            "game_id",
        ]


class ResourcesSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()

    class Meta:
        model = ResourceCount
        fields = ["item", "is_embedded", "percentage", "count"]


class WorldPollExtraSerializer(serializers.ModelSerializer):
    world_poll_id = serializers.IntegerField(source="id")
    world_poll_url = NestedHyperlinkedIdentityField(
        view_name="world-poll-detail",
        lookup_field=["world.id", "id"],
        lookup_url_kwarg=["world_id", "id"],
        read_only=True,
    )


class WorldPollLeaderboardSerializer(WorldPollExtraSerializer):
    leaderboard = LeaderboardSerializer(many=True)

    class Meta:
        model = WorldPoll
        fields = ["world_poll_id", "world_poll_url", "leaderboard"]


class WorldPollResourcesSerializer(WorldPollExtraSerializer):
    resources = ResourcesSerializer(many=True)

    class Meta:
        model = WorldPoll
        fields = ["world_poll_id", "world_poll_url", "resources"]


class WorldBlockColorSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()
    color = SimpleColorSerializer()

    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
            "color",
            "is_new_color",
            "exist_on_perm",
            "exist_via_transform",
        ]


class WorldDistanceSerializer(serializers.ModelSerializer):
    world_source = SimpleWorldSerializer()
    world_dest = SimpleWorldSerializer()
    cost = serializers.IntegerField()
    min_portal_cost = serializers.IntegerField(allow_null=True)
    min_portal_open_cost = serializers.IntegerField(allow_null=True)
    min_conduits = serializers.IntegerField(allow_null=True)

    class Meta:
        model = WorldDistance
        fields = [
            "world_source",
            "world_dest",
            "distance",
            "cost",
            "min_portal_cost",
            "min_portal_open_cost",
            "min_conduits",
        ]


class BlockColorSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()
    world = SimpleWorldSerializer()

    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
            "world",
            "is_new_color",
            "exist_on_perm",
            "exist_via_transform",
        ]


class ItemColorSerializer(serializers.ModelSerializer):
    color = SimpleColorSerializer()
    world = SimpleWorldSerializer()

    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
            "world",
            "is_new_color",
            "exist_on_perm",
            "exist_via_transform",
        ]


class WorldBlockColorsViewSerializer(serializers.ModelSerializer):
    world_url = serializers.HyperlinkedIdentityField(
        view_name="world-detail",
        lookup_field="id",
        read_only=True,
    )
    block_colors = WorldBlockColorSerializer(
        many=True, read_only=True, source="worldblockcolor_set"
    )

    class Meta:
        model = World
        fields = ["world_url", "block_colors"]


class WorldPollSerializer(serializers.ModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name="world-poll-detail",
        lookup_field=["world.id", "id"],
        lookup_url_kwarg=["world_id", "id"],
        read_only=True,
    )
    leaderboard_url = NestedHyperlinkedIdentityField(
        view_name="world-poll-leaderboard",
        lookup_field=["world.id", "id"],
        lookup_url_kwarg=["world_id", "id"],
        read_only=True,
    )
    resources_url = NestedHyperlinkedIdentityField(
        view_name="world-poll-resources",
        lookup_field=["world.id", "id"],
        lookup_url_kwarg=["world_id", "id"],
        read_only=True,
    )
    world = SimpleWorldSerializer()

    player_count = serializers.IntegerField(
        source="result.player_count",
        read_only=True,
    )
    beacon_count = serializers.IntegerField(
        source="result.beacon_count",
        read_only=True,
    )
    plot_count = serializers.IntegerField(
        source="result.plot_count",
        read_only=True,
    )
    total_prestige = serializers.IntegerField(
        source="result.total_prestige", read_only=True
    )

    class Meta:
        model = WorldPoll
        fields = [
            "url",
            "id",
            "leaderboard_url",
            "resources_url",
            "time",
            "world",
            "player_count",
            "beacon_count",
            "plot_count",
            "total_prestige",
        ]


class ItemResourceCountTimeSeriesTBSerializer(NullSerializer):
    time_bucket = serializers.DateTimeField(required=False)
    count_average = serializers.FloatField()
    count_mode = serializers.IntegerField()
    count_median = serializers.IntegerField()
    count_min = serializers.IntegerField()
    count_max = serializers.IntegerField()
    count_stddev = serializers.FloatField()
    count_variance = serializers.FloatField()


class WorldPollTBSerializer(NullSerializer):
    time_bucket = serializers.DateTimeField(required=False)

    player_count_average = serializers.FloatField(
        source="worldpollresult__player_count_average",
    )
    player_count_mode = serializers.IntegerField(
        source="worldpollresult__player_count_mode"
    )
    player_count_median = serializers.IntegerField(
        source="worldpollresult__player_count_median"
    )
    player_count_min = serializers.IntegerField(
        source="worldpollresult__player_count_min"
    )
    player_count_max = serializers.IntegerField(
        source="worldpollresult__player_count_max"
    )
    player_count_stddev = serializers.FloatField(
        source="worldpollresult__player_count_stddev",
    )
    player_count_variance = serializers.FloatField(
        source="worldpollresult__player_count_variance",
    )

    beacon_count_average = serializers.FloatField(
        source="worldpollresult__beacon_count_average",
    )
    beacon_count_mode = serializers.IntegerField(
        source="worldpollresult__beacon_count_mode"
    )
    beacon_count_median = serializers.IntegerField(
        source="worldpollresult__beacon_count_median"
    )
    beacon_count_min = serializers.IntegerField(
        source="worldpollresult__beacon_count_min"
    )
    beacon_count_max = serializers.IntegerField(
        source="worldpollresult__beacon_count_max"
    )
    beacon_count_stddev = serializers.FloatField(
        source="worldpollresult__beacon_count_stddev",
    )
    beacon_count_variance = serializers.FloatField(
        source="worldpollresult__beacon_count_variance",
    )

    plot_count_average = serializers.FloatField(
        source="worldpollresult__plot_count_average",
    )
    plot_count_mode = serializers.IntegerField(
        source="worldpollresult__plot_count_mode"
    )
    plot_count_median = serializers.IntegerField(
        source="worldpollresult__plot_count_median"
    )
    plot_count_min = serializers.IntegerField(
        source="worldpollresult__plot_count_min"
    )
    plot_count_max = serializers.IntegerField(
        source="worldpollresult__plot_count_max"
    )
    plot_count_stddev = serializers.FloatField(
        source="worldpollresult__plot_count_stddev",
    )
    plot_count_variance = serializers.FloatField(
        source="worldpollresult__plot_count_variance",
    )

    total_prestige_average = serializers.FloatField(
        source="worldpollresult__total_prestige_average",
    )
    total_prestige_mode = serializers.IntegerField(
        source="worldpollresult__total_prestige_mode"
    )
    total_prestige_median = serializers.IntegerField(
        source="worldpollresult__total_prestige_median"
    )
    total_prestige_min = serializers.IntegerField(
        source="worldpollresult__total_prestige_min"
    )
    total_prestige_max = serializers.IntegerField(
        source="worldpollresult__total_prestige_max"
    )
    total_prestige_stddev = serializers.FloatField(
        source="worldpollresult__total_prestige_stddev",
    )
    total_prestige_variance = serializers.FloatField(
        source="worldpollresult__total_prestige_variance",
    )


class SimpleWorldShopPriceSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()
    location = LocationSerializer()


class SimpleWorldShopStandPriceSerializer(SimpleWorldShopPriceSerializer):
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


class SimpleWorldRequestBasketPriceSerializer(SimpleWorldShopPriceSerializer):
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


class SimpleItemShopPriceSerializer(serializers.ModelSerializer):
    world = SimpleWorldSerializer()
    location = LocationSerializer()


class SimpleItemShopStandPriceSerializer(SimpleItemShopPriceSerializer):
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


class SimpleItemRequestBasketPriceSerializer(SimpleItemShopPriceSerializer):
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
