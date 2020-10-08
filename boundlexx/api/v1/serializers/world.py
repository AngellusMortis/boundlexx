from rest_framework import serializers

from boundlexx.api.common.serializers import (
    NullSerializer,
    SimpleWorldSerializer,
    WorldSerializer,
)
from boundlexx.api.v1.serializers.base import (
    NestedHyperlinkedIdentityField,
    RequestBasketsURL,
    ShopStandsURL,
    SimpleColorSerializer,
    URLSimpleItemSerializer,
    URLSimpleSkillSerializer,
    URLSimpleWorldSerializer,
)
from boundlexx.boundless.models import (
    LeaderboardRecord,
    ResourceCount,
    World,
    WorldBlockColor,
    WorldDistance,
    WorldPoll,
)


class URLWorldSerializer(WorldSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="world-detail",
        lookup_field="id",
    )
    polls_url = NestedHyperlinkedIdentityField(
        view_name="world-poll-list",
        lookup_field=["id"],
        lookup_url_kwarg=["world_id"],
    )
    block_colors_url = serializers.HyperlinkedIdentityField(
        view_name="world-block-colors",
        lookup_field="id",
    )
    distances_url = NestedHyperlinkedIdentityField(
        view_name="world-distance-list",
        lookup_field=["id"],
        lookup_url_kwarg=["world_source__id"],
    )
    request_baskets_url = RequestBasketsURL()
    shop_stands_url = ShopStandsURL()
    assignment = URLSimpleWorldSerializer(allow_null=True)
    protection_skill = URLSimpleSkillSerializer()

    class Meta:
        model = World
        fields = [
            "url",
            "id",
            "polls_url",
            "block_colors_url",
            "distances_url",
            "request_baskets_url",
            "next_request_basket_update",
            "shop_stands_url",
            "next_shop_stand_update",
            "active",
            "name",
            "display_name",
            "text_name",
            "html_name",
            "address",
            "image_url",
            "forum_url",
            "assignment",
            "region",
            "tier",
            "size",
            "world_type",
            "special_type",
            "protection_points",
            "protection_skill",
            "time_offset",
            "is_sovereign",
            "is_perm",
            "is_exo",
            "is_creative",
            "is_locked",
            "is_public",
            "is_public_edit",
            "is_public_claim",
            "is_finalized",
            "number_of_regions",
            "start",
            "end",
            "atmosphere_color",
            "water_color",
            "surface_liquid",
            "core_liquid",
            "bows",
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderboardRecord
        fields = ["world_rank", "guild_tag", "mayor_name", "name", "prestige"]


class ResourcesSerializer(serializers.ModelSerializer):
    item = URLSimpleItemSerializer()

    class Meta:
        model = ResourceCount
        fields = ["item", "is_embedded", "percentage", "count", "average_per_chunk"]


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
    item = URLSimpleItemSerializer()
    color = SimpleColorSerializer()

    is_perm = serializers.BooleanField()
    is_sovereign_only = serializers.BooleanField()
    is_exo_only = serializers.BooleanField()
    days_since_exo = serializers.IntegerField(allow_null=True)
    days_since_transform_exo = serializers.IntegerField(allow_null=True)
    first_world = URLSimpleWorldSerializer(allow_null=True)
    last_exo = URLSimpleWorldSerializer(allow_null=True)
    transform_first_world = URLSimpleWorldSerializer(allow_null=True)
    transform_last_exo = URLSimpleWorldSerializer(allow_null=True)

    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
            "color",
            "active",
            "is_default",
            "is_perm",
            "is_sovereign_only",
            "is_exo_only",
            "is_new",
            "is_new_exo",
            "is_new_transform",
            "days_since_exo",
            "days_since_transform_exo",
            "first_world",
            "last_exo",
            "transform_first_world",
            "transform_last_exo",
        ]


class WorldDistanceSerializer(serializers.ModelSerializer):
    world_source = URLSimpleWorldSerializer()
    world_dest = URLSimpleWorldSerializer()
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
    item = URLSimpleItemSerializer()
    world = URLSimpleWorldSerializer()

    is_perm = serializers.BooleanField()
    is_sovereign_only = serializers.BooleanField()
    is_exo_only = serializers.BooleanField()
    days_since_exo = serializers.IntegerField(allow_null=True)
    days_since_transform_exo = serializers.IntegerField(allow_null=True)
    first_world = URLSimpleWorldSerializer(allow_null=True)
    last_exo = URLSimpleWorldSerializer(allow_null=True)
    transform_first_world = URLSimpleWorldSerializer(allow_null=True)
    transform_last_exo = URLSimpleWorldSerializer(allow_null=True)

    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
            "world",
            "active",
            "is_default",
            "is_perm",
            "is_sovereign_only",
            "is_exo_only",
            "is_new",
            "is_new_exo",
            "is_new_transform",
            "days_since_exo",
            "days_since_transform_exo",
            "first_world",
            "last_exo",
            "transform_first_world",
            "transform_last_exo",
        ]


class ItemColorSerializer(serializers.ModelSerializer):
    color = SimpleColorSerializer()

    is_perm = serializers.BooleanField()
    is_sovereign_only = serializers.BooleanField()
    is_exo_only = serializers.BooleanField()
    days_since_exo = serializers.IntegerField(allow_null=True)
    days_since_transform_exo = serializers.IntegerField(allow_null=True)
    first_world = URLSimpleWorldSerializer(allow_null=True)
    last_exo = URLSimpleWorldSerializer(allow_null=True)
    transform_first_world = URLSimpleWorldSerializer(allow_null=True)
    transform_last_exo = URLSimpleWorldSerializer(allow_null=True)

    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
            "active",
            "is_default",
            "is_perm",
            "is_sovereign_only",
            "is_exo_only",
            "is_new",
            "is_new_exo",
            "is_new_transform",
            "days_since_exo",
            "days_since_transform_exo",
            "first_world",
            "last_exo",
            "transform_first_world",
            "transform_last_exo",
        ]


class PossibleColorSerializer(serializers.ModelSerializer):
    color = SimpleColorSerializer()

    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
        ]


class PossibleItemSerializer(serializers.ModelSerializer):
    item = URLSimpleItemSerializer()

    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
        ]


class WorldColorSerializer(serializers.ModelSerializer):
    world = URLSimpleWorldSerializer()

    is_perm = serializers.BooleanField()
    is_sovereign_only = serializers.BooleanField()
    is_exo_only = serializers.BooleanField()
    days_since_exo = serializers.IntegerField(allow_null=True)
    days_since_transform_exo = serializers.IntegerField(allow_null=True)
    first_world = URLSimpleWorldSerializer(allow_null=True)
    last_exo = URLSimpleWorldSerializer(allow_null=True)
    transform_first_world = URLSimpleWorldSerializer(allow_null=True)
    transform_last_exo = URLSimpleWorldSerializer(allow_null=True)

    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
            "world",
            "active",
            "is_default",
            "is_perm",
            "is_sovereign_only",
            "is_exo_only",
            "is_new",
            "is_new_exo",
            "is_new_transform",
            "days_since_exo",
            "days_since_transform_exo",
            "first_world",
            "last_exo",
            "transform_first_world",
            "transform_last_exo",
        ]


class WorldBlockColorsViewSerializer(
    serializers.Serializer
):  # pylint: disable=abstract-method
    world_url = serializers.HyperlinkedIdentityField(
        view_name="world-detail",
        lookup_field="id",
        read_only=True,
    )
    block_colors = WorldBlockColorSerializer(many=True, read_only=True)


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
    world = URLSimpleWorldSerializer()

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
    plot_count_min = serializers.IntegerField(source="worldpollresult__plot_count_min")
    plot_count_max = serializers.IntegerField(source="worldpollresult__plot_count_max")
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


class KindOfSimpleWorldSerializer(SimpleWorldSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="world-detail",
        lookup_field="id",
    )

    class Meta:
        model = World
        fields = [
            "url",
            "id",
            "active",
            "image_url",
            "display_name",
            "text_name",
            "html_name",
            "tier",
            "size",
            "world_type",
            "special_type",
            "is_sovereign",
            "is_perm",
            "is_exo",
            "is_creative",
            "is_locked",
        ]
