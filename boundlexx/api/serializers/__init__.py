from typing import Optional

from rest_framework import serializers

from boundlexx.api.serializers.base import NullSerializer, SimpleWorldSerializer
from boundlexx.api.serializers.game import (
    BlockSerialzier,
    ColorSerializer,
    EmojiSerializer,
    GameFileSerializer,
    ItemResourceCountSerializer,
    ItemResourceCountTimeSeriesSerializer,
    ItemSerializer,
    RecipeGroupSerializer,
    RecipeSerializer,
    SimpleGameFileSerializer,
    SimpleItemRequestBasketPriceSerializer,
    SimpleItemShopPriceSerializer,
    SimpleItemShopStandPriceSerializer,
    SimpleWorldRequestBasketPriceSerializer,
    SimpleWorldShopPriceSerializer,
    SimpleWorldShopStandPriceSerializer,
    SkillGroupSerializer,
    SkillSerializer,
    SubtitleSerializer,
)
from boundlexx.api.serializers.world import (
    BlockColorSerializer,
    ItemColorSerializer,
    ItemResourceCountTimeSeriesTBSerializer,
    KindOfSimpleWorldSerializer,
    LeaderboardSerializer,
    PossibleColorSerializer,
    PossibleItemSerializer,
    ResourcesSerializer,
    WorldBlockColorSerializer,
    WorldBlockColorsViewSerializer,
    WorldColorSerializer,
    WorldDistanceSerializer,
    WorldPollExtraSerializer,
    WorldPollLeaderboardSerializer,
    WorldPollResourcesSerializer,
    WorldPollSerializer,
    WorldPollTBSerializer,
    WorldSerializer,
)
from boundlexx.boundless.models import World, WorldPoll

__all__ = [
    "BlockColorSerializer",
    "BlockSerialzier",
    "ColorSerializer",
    "EmojiSerializer",
    "ForumFormatPostSerialzier",
    "ForumFormatSerialzier",
    "ForumFormatSerialzier",
    "GameFileSerializer",
    "ItemColorSerializer",
    "ItemResourceCountSerializer",
    "ItemResourceCountTimeSeriesSerializer",
    "ItemResourceCountTimeSeriesTBSerializer",
    "ItemSerializer",
    "KindOfSimpleWorldSerializer",
    "LeaderboardSerializer",
    "PossibleColorSerializer",
    "PossibleItemSerializer",
    "RecipeGroupSerializer",
    "RecipeSerializer",
    "ResourcesSerializer",
    "SimpleGameFileSerializer",
    "SimpleItemRequestBasketPriceSerializer",
    "SimpleItemShopPriceSerializer",
    "SimpleItemShopStandPriceSerializer",
    "SimpleWorldRequestBasketPriceSerializer",
    "SimpleWorldSerializer",
    "SimpleWorldShopPriceSerializer",
    "SimpleWorldShopStandPriceSerializer",
    "SkillGroupSerializer",
    "SkillSerializer",
    "SubtitleSerializer",
    "WorldBlockColorSerializer",
    "WorldBlockColorsViewSerializer",
    "WorldColorSerializer",
    "WorldDistanceSerializer",
    "WorldPollExtraSerializer",
    "WorldPollLeaderboardSerializer",
    "WorldPollResourcesSerializer",
    "WorldPollSerializer",
    "WorldPollTBSerializer",
    "WorldSerializer",
]

BASE_QUERY = World.objects.all().select_related("assignment")


class ForumFormatPostSerialzier(NullSerializer):
    username = serializers.CharField(
        required=False,
        help_text="Your Boundless Username. Required for Sovereign worlds.",
    )
    world_id = serializers.IntegerField(
        required=True,
        help_text=(
            "The ID of your world if 'World Name' is not working. You can get "
            'your World ID from the <a href="https://forum.playboundless.com/'
            "uploads/default/original/3X/3/f/3fef2e21cedc3d4594971d6143d40110bd489686"
            '.jpeg" target="_blank">Debug Menu</a> if you are on PC'
        ),
        label="World ID",
    )
    will_renew = serializers.NullBooleanField(
        required=False,
        help_text="Do you plan to renew this world? Required for Sovereign worlds.",
        label="Will Renew?",
    )
    compactness = serializers.NullBooleanField(
        required=False,
        help_text="Is Beacon compactness enabled?",
        label="Beacon Compactness?",
    )
    can_visit = serializers.BooleanField(
        required=False,
        help_text=(
            "Can Everyone warp/use portals to your world? "
            "Required for Sovereign worlds."
        ),
        label="Can Visit?",
    )
    can_edit = serializers.BooleanField(
        required=False,
        help_text=(
            "Can Everyone edit blocks on your world (outside of plots)?"
            " Required for Sovereign worlds."
        ),
        label="Can Edit?",
    )
    can_claim = serializers.BooleanField(
        required=False,
        help_text=(
            "Can Everyone create beacon and plot on your world? "
            "Required for Sovereign worlds."
        ),
        label="Can Claim?",
    )
    portal_directions = serializers.CharField(
        required=False,
        max_length=100,
        help_text=(
            "Directions to help players find the portal to your world."
            "Required for Sovereign worlds."
        ),
        label="Portal Directions",
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

    def validate(self, attrs):
        if self.world.is_sovereign:  # type: ignore
            errors = {}
            for key in [
                "username",
                "will_renew",
                "portal_directions",
                "can_visit",
                "can_edit",
                "can_claim",
            ]:
                if key not in attrs:
                    errors[key] = "Required if Sovereign world"
            if len(errors) > 0:
                raise serializers.ValidationError(errors)

        return attrs


class ForumFormatSerialzier(NullSerializer):
    title = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True)


class WorldPollDetailSerializer(WorldPollSerializer):
    resources = ResourcesSerializer(many=True, source="resourcecount_set")
    leaderboard = LeaderboardSerializer(many=True, source="leaderboardrecord_set")

    class Meta:
        model = WorldPoll
        fields = [
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


class WorldDumpSerializer(WorldSerializer):
    block_colors = WorldBlockColorSerializer(many=True, source="active_colors")
    latest_poll = WorldPollDetailSerializer(many=True)

    class Meta:
        model = World
        fields = [
            "id",
            "active",
            "name",
            "display_name",
            "address",
            "image_url",
            "forum_url",
            "assignment",
            "region",
            "tier",
            "size",
            "world_type",
            "protection_points",
            "protection_skill",
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
            "block_colors",
            "latest_poll",
        ]
