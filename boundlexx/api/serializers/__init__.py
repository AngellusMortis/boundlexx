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
    LeaderboardSerializer,
    PossibleColorSerializer,
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
    "ForumFormatSerialzier",
    "GameFileSerializer",
    "ItemColorSerializer",
    "ItemResourceCountSerializer",
    "ItemResourceCountTimeSeriesSerializer",
    "ItemResourceCountTimeSeriesTBSerializer",
    "ItemSerializer",
    "LeaderboardSerializer",
    "PossibleColorSerializer",
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
