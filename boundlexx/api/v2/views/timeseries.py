from django.conf import settings
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from boundlexx.api.common.mixins import TimeseriesMixin
from boundlexx.api.common.serializers import (
    ItemResourceCountTimeSeriesSerializer,
    ItemResourceCountTimeSeriesTBSerializer,
    WorldPollLeaderboardSerializer,
    WorldPollResourcesSerializer,
    WorldPollSerializer,
    WorldPollTBSerializer,
)
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.boundless.models import ResourceCount, WorldPoll


class ItemResourceTimeseriesViewSet(
    TimeseriesMixin, NestedViewSetMixin, BoundlexxViewSet
):
    schema = DescriptiveAutoSchema(tags=["Items", "Timeseries"])
    queryset = ResourceCount.objects.filter(
        world_poll__world__active=True,
        world_poll__world__is_public=True,
        world_poll__world__is_creative=False,
    ).select_related("world_poll", "world_poll__world", "item", "item__resource_data")
    serializer_class = ItemResourceCountTimeSeriesSerializer
    time_bucket_serializer_class = ItemResourceCountTimeSeriesTBSerializer
    number_fields = ["count"]
    lookup_field = "id"

    def get_queryset(self):
        item_id = self.kwargs.get("id")

        if item_id not in settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING:
            raise Http404

        queryset = super().get_queryset()

        return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list resource counts for a give item/world combination
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.operation_id = "listItemResourceTimeseries"  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a specific resource counts for a give item/world combination
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.operation_id = "retrieveItemResourceTimeseries"  # type: ignore # noqa E501


class WorldPollViewSet(TimeseriesMixin, NestedViewSetMixin, BoundlexxViewSet):
    schema = DescriptiveAutoSchema(tags=["Worlds", "Timeseries"])
    queryset = (
        WorldPoll.objects.all()
        .select_related("world")
        .prefetch_related(
            "worldpollresult_set",
            "leaderboardrecord_set",
            "resourcecount_set",
            "resourcecount_set__item",
        )
    )
    serializer_class = WorldPollSerializer
    time_bucket_serializer_class = WorldPollTBSerializer
    number_fields = [
        "worldpollresult__player_count",
        "worldpollresult__beacon_count",
        "worldpollresult__plot_count",
        "worldpollresult__total_prestige",
    ]
    lookup_field = "id"

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list polls avaiable for give World
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a specific poll for a given world

        Can pass `latest` or `initial` in place of `id` to retrieve the
        newest or first one
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    @action(
        detail=True,
        methods=["get"],
        serializer_class=WorldPollLeaderboardSerializer,
    )
    def leaderboard(
        self,
        request,
        world_id=None,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Retrieves the leaderboard for a given world poll result
        """

        world_poll = self.get_object()

        serializer = self.get_serializer_class()(
            world_poll, context={"request": request}
        )

        return Response(serializer.data)

    leaderboard.operation_id = "listWorldPollLeaderboards"

    @action(
        detail=True,
        methods=["get"],
        serializer_class=WorldPollResourcesSerializer,
    )
    def resources(
        self,
        request,
        world_id=None,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Retrieves the count of resources for a given world poll result
        """
        world_poll = self.get_object()

        serializer = self.get_serializer_class()(
            world_poll, context={"request": request}
        )

        return Response(serializer.data)

    resources.operation_id = "listWorldPollResources"
