from boundlexx.api.common.serializers import (
    LeaderboardSerializer,
    ResourcesSerializer,
    WorldPollSerializer,
)
from boundlexx.api.v1.serializers.base import URLSimpleWorldSerializer
from boundlexx.api.v1.serializers.game import (
    URLBlockSerializer,
    URLColorSerializer,
    URLEmojiSerializer,
    URLItemRequestBasketPriceSerializer,
    URLItemResourceCountSerializer,
    URLItemResourceCountTimeSeriesSerializer,
    URLItemSerializer,
    URLItemShopStandPriceSerializer,
    URLMetalSerializer,
    URLRecipeGroupSerializer,
    URLRecipeSerializer,
    URLSkillGroupSerializer,
    URLSkillSerializer,
    URLWorldRequestBasketPriceSerializer,
    URLWorldShopStandPriceSerializer,
)
from boundlexx.api.v1.serializers.world import (
    KindOfSimpleWorldSerializer,
    PossibleColorSerializer,
    PossibleItemSerializer,
    URLBlockColorSerializer,
    URLItemColorSerializer,
    URLWorldBlockColorSerializer,
    URLWorldColorSerializer,
    URLWorldDistanceSerializer,
    URLWorldPollLeaderboardSerializer,
    URLWorldPollResourcesSerializer,
    URLWorldPollSerializer,
    URLWorldSerializer,
    WorldBlockColorsViewSerializer,
)
from boundlexx.boundless.models import WorldPoll

__all__ = [
    "KindOfSimpleWorldSerializer",
    "PossibleColorSerializer",
    "PossibleItemSerializer",
    "URLBlockColorSerializer",
    "URLBlockSerializer",
    "URLColorSerializer",
    "URLEmojiSerializer",
    "URLItemColorSerializer",
    "URLItemRequestBasketPriceSerializer",
    "URLItemResourceCountSerializer",
    "URLItemResourceCountTimeSeriesSerializer",
    "URLItemSerializer",
    "URLItemShopStandPriceSerializer",
    "URLMetalSerializer",
    "URLRecipeGroupSerializer",
    "URLRecipeSerializer",
    "URLSimpleWorldSerializer",
    "URLSkillGroupSerializer",
    "URLSkillSerializer",
    "URLWorldBlockColorSerializer",
    "URLWorldColorSerializer",
    "URLWorldDistanceSerializer",
    "URLWorldPollLeaderboardSerializer",
    "URLWorldPollResourcesSerializer",
    "URLWorldPollSerializer",
    "URLWorldRequestBasketPriceSerializer",
    "URLWorldSerializer",
    "URLWorldShopStandPriceSerializer",
    "WorldBlockColorsViewSerializer",
    "WorldPollDetailSerializer",
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
