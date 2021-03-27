from rest_framework import serializers

from boundlexx.api.common.serializers import (
    BlockColorSerializer,
    ItemColorSerializer,
    PossibleWBCSerializer,
    ResourcesSerializer,
    SimpleWorldSerializer,
    WorldBlockColorSerializer,
    WorldColorSerializer,
    WorldDistanceSerializer,
    WorldPollLeaderboardSerializer,
    WorldPollResourcesSerializer,
    WorldPollSerializer,
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
            "atlas_image_url",
        ]


class URLWorldPollLeaderboardSerializer(WorldPollLeaderboardSerializer):
    world_poll_url = NestedHyperlinkedIdentityField(
        view_name="world-poll-detail",
        lookup_field=["world.id", "id"],
        lookup_url_kwarg=["world_id", "id"],
        read_only=True,
    )

    class Meta:
        model = WorldPoll
        fields = ["world_poll_id", "world_poll_url", "leaderboard"]


class URLResourcesSerializer(ResourcesSerializer):
    item = URLSimpleItemSerializer()

    class Meta:
        model = ResourceCount
        fields = ["item", "is_embedded", "percentage", "count", "average_per_chunk"]


class URLWorldPollResourcesSerializer(WorldPollResourcesSerializer):
    world_poll_url = NestedHyperlinkedIdentityField(
        view_name="world-poll-detail",
        lookup_field=["world.id", "id"],
        lookup_url_kwarg=["world_id", "id"],
        read_only=True,
    )
    resources = URLResourcesSerializer(many=True)

    class Meta:
        model = WorldPoll
        fields = ["world_poll_id", "world_poll_url", "resources"]


class URLWorldBlockColorSerializer(WorldBlockColorSerializer):
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


class URLWorldDistanceSerializer(WorldDistanceSerializer):
    world_source = URLSimpleWorldSerializer()
    world_dest = URLSimpleWorldSerializer()

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


class URLBlockColorSerializer(BlockColorSerializer):
    item = URLSimpleItemSerializer()
    world = URLSimpleWorldSerializer()

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


class URLItemColorSerializer(ItemColorSerializer):
    color = SimpleColorSerializer()
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


class PossibleColorSerializer(PossibleWBCSerializer):
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


class URLWorldColorSerializer(WorldColorSerializer):
    world = URLSimpleWorldSerializer()

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
    block_colors = URLWorldBlockColorSerializer(many=True, read_only=True)


class URLWorldPollSerializer(WorldPollSerializer):
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
            "name",
            "display_name",
            "text_name",
            "html_name",
            "world_class",
            "tier",
            "size",
            "world_type",
            "region",
            "address",
            "special_type",
            "is_sovereign",
            "is_perm",
            "is_exo",
            "is_creative",
            "is_locked",
            "is_public",
            "is_public_edit",
            "is_public_claim",
            "atlas_image_url",
        ]
