from boundlexx.api.v1.serializers.base import URLSimpleWorldSerializer
from boundlexx.api.v1.serializers.game import (
    ItemResourceCountTimeSeriesSerializer,
    URLBlockSerializer,
    URLColorSerializer,
    URLEmojiSerializer,
    URLItemRequestBasketPriceSerializer,
    URLItemResourceCountSerializer,
    URLItemSerializer,
    URLItemShopStandPriceSerializer,
    URLRecipeGroupSerializer,
    URLRecipeSerializer,
    URLSkillGroupSerializer,
    URLSkillSerializer,
    URLWorldRequestBasketPriceSerializer,
    URLWorldShopStandPriceSerializer,
)
from boundlexx.api.v1.serializers.world import (
    ItemResourceCountTimeSeriesTBSerializer,
    KindOfSimpleWorldSerializer,
    LeaderboardSerializer,
    PossibleColorSerializer,
    PossibleItemSerializer,
    ResourcesSerializer,
    URLBlockColorSerializer,
    URLItemColorSerializer,
    URLWorldBlockColorSerializer,
    URLWorldColorSerializer,
    URLWorldDistanceSerializer,
    URLWorldSerializer,
    WorldBlockColorsViewSerializer,
    WorldPollExtraSerializer,
    WorldPollLeaderboardSerializer,
    WorldPollResourcesSerializer,
    WorldPollSerializer,
    WorldPollTBSerializer,
)
from boundlexx.boundless.models import World, WorldPoll

__all__ = [
    "ItemResourceCountTimeSeriesSerializer",
    "ItemResourceCountTimeSeriesTBSerializer",
    "KindOfSimpleWorldSerializer",
    "LeaderboardSerializer",
    "PossibleColorSerializer",
    "PossibleItemSerializer",
    "ResourcesSerializer",
    "URLBlockColorSerializer",
    "URLBlockSerializer",
    "URLColorSerializer",
    "URLEmojiSerializer",
    "URLItemColorSerializer",
    "URLItemRequestBasketPriceSerializer",
    "URLItemResourceCountSerializer",
    "URLItemSerializer",
    "URLItemShopStandPriceSerializer",
    "URLRecipeGroupSerializer",
    "URLRecipeSerializer",
    "URLSimpleWorldSerializer",
    "URLSkillGroupSerializer",
    "URLSkillSerializer",
    "URLWorldBlockColorSerializer",
    "URLWorldColorSerializer",
    "URLWorldDistanceSerializer",
    "URLWorldRequestBasketPriceSerializer",
    "URLWorldSerializer",
    "URLWorldShopStandPriceSerializer",
    "WorldBlockColorsViewSerializer",
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
    block_colors = URLWorldBlockColorSerializer(many=True, source="active_colors")
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
