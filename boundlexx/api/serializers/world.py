from django.utils.translation import ugettext as _
from rest_framework import serializers

from boundlexx.api.serializers.base import (
    AzureImageField,
    NestedHyperlinkedIdentityField,
    NullSerializer,
    RequestBasketsURL,
    ShopStandsURL,
    SimpleColorSerializer,
    SimpleItemSerializer,
    SimpleSkillSerializer,
    SimpleWorldSerializer,
)
from boundlexx.boundless.models import (
    LeaderboardRecord,
    ResourceCount,
    World,
    WorldBlockColor,
    WorldDistance,
    WorldPoll,
)


class BowSerializer(NullSerializer):
    best = serializers.ListField(child=serializers.CharField())
    neutral = serializers.ListField(child=serializers.CharField())
    lucent = serializers.ListField(child=serializers.CharField())


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
    request_baskets_url = RequestBasketsURL()
    shop_stands_url = ShopStandsURL()
    assignment = SimpleWorldSerializer()
    image_url = AzureImageField(source="image", allow_null=True)
    forum_url = serializers.URLField(allow_null=True)

    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    bows = BowSerializer()

    protection_points = serializers.IntegerField(
        allow_null=True,
        help_text=_(
            "'points' are not equal to levels in skill. For more details see "
            '<a href="https://forum.playboundless.com/t/28068/4">this forum '
            "post</a>."
        ),
    )
    protection_skill = SimpleSkillSerializer()

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
    item = SimpleItemSerializer()

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
    item = SimpleItemSerializer()
    color = SimpleColorSerializer()

    is_perm = serializers.BooleanField()
    is_sovereign_only = serializers.BooleanField()
    is_exo_only = serializers.BooleanField()
    days_since_exo = serializers.IntegerField(allow_null=True)
    days_since_transform_exo = serializers.IntegerField(allow_null=True)
    first_world = SimpleWorldSerializer(allow_null=True)
    last_exo = SimpleWorldSerializer(allow_null=True)
    transform_first_world = SimpleWorldSerializer(allow_null=True)
    transform_last_exo = SimpleWorldSerializer(allow_null=True)

    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
            "color",
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

    is_perm = serializers.BooleanField()
    is_sovereign_only = serializers.BooleanField()
    is_exo_only = serializers.BooleanField()
    days_since_exo = serializers.IntegerField(allow_null=True)
    days_since_transform_exo = serializers.IntegerField(allow_null=True)
    first_world = SimpleWorldSerializer(allow_null=True)
    last_exo = SimpleWorldSerializer(allow_null=True)
    transform_first_world = SimpleWorldSerializer(allow_null=True)
    transform_last_exo = SimpleWorldSerializer(allow_null=True)

    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
            "world",
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
    first_world = SimpleWorldSerializer(allow_null=True)
    last_exo = SimpleWorldSerializer(allow_null=True)
    transform_first_world = SimpleWorldSerializer(allow_null=True)
    transform_last_exo = SimpleWorldSerializer(allow_null=True)

    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
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
    item = SimpleItemSerializer()

    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
        ]


class WorldColorSerializer(serializers.ModelSerializer):
    world = SimpleWorldSerializer()

    is_perm = serializers.BooleanField()
    is_sovereign_only = serializers.BooleanField()
    is_exo_only = serializers.BooleanField()
    days_since_exo = serializers.IntegerField(allow_null=True)
    days_since_transform_exo = serializers.IntegerField(allow_null=True)
    first_world = SimpleWorldSerializer(allow_null=True)
    last_exo = SimpleWorldSerializer(allow_null=True)
    transform_first_world = SimpleWorldSerializer(allow_null=True)
    transform_last_exo = SimpleWorldSerializer(allow_null=True)

    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
            "world",
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


class KindOfSimpleWorldSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="world-detail",
        lookup_field="id",
        read_only=True,
    )

    class Meta:
        model = World
        fields = [
            "url",
            "id",
            "display_name",
            "text_name",
            "html_name",
            "tier",
            "world_type",
            "special_type",
            "is_sovereign",
            "is_perm",
            "is_exo",
            "is_creative",
            "is_locked",
        ]
