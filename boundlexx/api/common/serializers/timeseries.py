from rest_framework import serializers

from boundlexx.api.common.serializers.base import NullSerializer
from boundlexx.api.common.serializers.item import (
    IDItemSerializer,
    ItemResourceCountSerializer,
)
from boundlexx.api.common.serializers.world import IDWorldSerializer
from boundlexx.boundless.models import LeaderboardRecord, ResourceCount, WorldPoll


class ItemResourceCountTimeSeriesSerializer(ItemResourceCountSerializer):
    time = serializers.DateTimeField()

    class Meta:
        model = ResourceCount
        fields = [
            "time",
            "world",
            "is_embedded",
            "percentage",
            "count",
            "average_per_chunk",
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


class WorldPollSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # noqa: A003
    time = serializers.DateTimeField()

    world = IDWorldSerializer()

    player_count = serializers.IntegerField(
        source="result.player_count",
    )
    beacon_count = serializers.IntegerField(
        source="result.beacon_count",
    )
    plot_count = serializers.IntegerField(
        source="result.plot_count",
    )
    total_prestige = serializers.IntegerField(source="result.total_prestige")

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
        ]


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


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderboardRecord
        fields = ["world_rank", "guild_tag", "mayor_name", "name", "prestige"]


class ResourcesSerializer(serializers.ModelSerializer):
    item = IDItemSerializer()
    is_embedded = serializers.BooleanField()

    class Meta:
        model = ResourceCount
        fields = ["item", "is_embedded", "percentage", "count", "average_per_chunk"]


class WorldPollExtraSerializer(serializers.ModelSerializer):
    world_poll_id = serializers.IntegerField(source="id")


class WorldPollLeaderboardSerializer(WorldPollExtraSerializer):
    leaderboard = LeaderboardSerializer(many=True)

    class Meta:
        model = WorldPoll
        fields = ["world_poll_id", "leaderboard"]


class WorldPollResourcesSerializer(WorldPollExtraSerializer):
    resources = ResourcesSerializer(many=True)

    class Meta:
        model = WorldPoll
        fields = ["world_poll_id", "resources"]
