from boundlexx.api.v1.serializers.base import URLSimpleWorldSerializer
from boundlexx.api.v1.serializers.game import (
    ItemResourceCountSerializer,
    ItemResourceCountTimeSeriesSerializer,
    RecipeGroupSerializer,
    RecipeSerializer,
    SimpleItemRequestBasketPriceSerializer,
    SimpleItemShopPriceSerializer,
    SimpleItemShopStandPriceSerializer,
    SimpleWorldRequestBasketPriceSerializer,
    SimpleWorldShopPriceSerializer,
    SimpleWorldShopStandPriceSerializer,
    URLBlockSerializer,
    URLColorSerializer,
    URLEmojiSerializer,
    URLItemSerializer,
    URLSkillGroupSerializer,
    URLSkillSerializer,
)
from boundlexx.api.v1.serializers.world import (
    BlockColorSerializer,
    ItemColorSerializer,
    ItemResourceCountTimeSeriesTBSerializer,
    KindOfSimpleWorldSerializer,
    LeaderboardSerializer,
    PossibleColorSerializer,
    PossibleItemSerializer,
    ResourcesSerializer,
    URLWorldSerializer,
    WorldBlockColorSerializer,
    WorldBlockColorsViewSerializer,
    WorldColorSerializer,
    WorldDistanceSerializer,
    WorldPollExtraSerializer,
    WorldPollLeaderboardSerializer,
    WorldPollResourcesSerializer,
    WorldPollSerializer,
    WorldPollTBSerializer,
)
from boundlexx.boundless.models import World, WorldPoll

__all__ = [
    "BlockColorSerializer",
    "ItemColorSerializer",
    "ItemResourceCountSerializer",
    "ItemResourceCountTimeSeriesSerializer",
    "ItemResourceCountTimeSeriesTBSerializer",
    "KindOfSimpleWorldSerializer",
    "LeaderboardSerializer",
    "PossibleColorSerializer",
    "PossibleItemSerializer",
    "RecipeGroupSerializer",
    "RecipeSerializer",
    "ResourcesSerializer",
    "SimpleItemRequestBasketPriceSerializer",
    "SimpleItemShopPriceSerializer",
    "SimpleItemShopStandPriceSerializer",
    "SimpleWorldRequestBasketPriceSerializer",
    "SimpleWorldShopPriceSerializer",
    "SimpleWorldShopStandPriceSerializer",
    "URLBlockSerializer",
    "URLColorSerializer",
    "URLEmojiSerializer",
    "URLItemSerializer",
    "URLSimpleWorldSerializer",
    "URLSkillGroupSerializer",
    "URLSkillSerializer",
    "URLWorldSerializer",
    "WorldBlockColorSerializer",
    "WorldBlockColorsViewSerializer",
    "WorldColorSerializer",
    "WorldDistanceSerializer",
    "WorldDumpSerializer",
    "WorldPollDetailSerializer",
    "WorldPollExtraSerializer",
    "WorldPollLeaderboardSerializer",
    "WorldPollResourcesSerializer",
    "WorldPollSerializer",
    "WorldPollTBSerializer",
]


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


class WorldDumpSerializer(URLWorldSerializer):
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
