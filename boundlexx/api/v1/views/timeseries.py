from django.http import Http404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from boundlexx.api.common.mixins import TimeseriesMixin
from boundlexx.api.common.serializers import (
    ItemResourceCountTimeSeriesTBSerializer,
    WorldPollTBSerializer,
)
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.examples import world as wexamples
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.v1.serializers import (
    URLItemResourceCountTimeSeriesSerializer,
    URLWorldPollLeaderboardSerializer,
    URLWorldPollResourcesSerializer,
    URLWorldPollSerializer,
)
from boundlexx.boundless.models import ResourceCount, WorldPoll

ITEM_RESOURCE_TIMESERIES_EXAMPLE = {
    "time": "2020-08-04T09:09:50.136765-04:00",
    "url": f"{get_base_url()}/api/v1/items/32779/resource-counts/1/",
    "item_url": f"{get_base_url()}/api/v1/items/32779/",
    "world": {
        "url": f"{get_base_url()}/api/v1/worlds/1/",
        "id": 1,
        "display_name": "Sochaltin I",
    },
    "count": 6051899,
}


class ItemResourceTimeseriesViewSet(
    TimeseriesMixin, NestedViewSetMixin, BoundlexxViewSet
):
    schema = DescriptiveAutoSchema(tags=["Items", "Timeseries"])
    queryset = ResourceCount.objects.filter(
        world_poll__world__active=True,
        world_poll__world__is_public=True,
        world_poll__world__is_creative=False,
    ).select_related("world_poll", "world_poll__world", "item", "item__resource_data")
    serializer_class = URLItemResourceCountTimeSeriesSerializer
    time_bucket_serializer_class = ItemResourceCountTimeSeriesTBSerializer
    number_fields = ["count"]
    lookup_field = "id"

    def get_queryset(self):
        queryset = super().get_queryset()

        if queryset.count() == 0:
            raise Http404

        return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list resource counts for a give item/world combination
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(ITEM_RESOURCE_TIMESERIES_EXAMPLE)}}  # type: ignore # noqa E501
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

    retrieve.example = {"retrieve": {"value": ITEM_RESOURCE_TIMESERIES_EXAMPLE}}  # type: ignore # noqa E501
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
    serializer_class = URLWorldPollSerializer
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

    list.example = {"list": {"value": get_list_example(wexamples.WORLD_POLL_EXAMPLE)}}  # type: ignore # noqa E501

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

    retrieve.example = {"retrieve": {"value": wexamples.WORLD_POLL_EXAMPLE}}  # type: ignore # noqa E501

    @action(
        detail=True,
        methods=["get"],
        serializer_class=URLWorldPollLeaderboardSerializer,
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

    leaderboard.example = {
        "leaderboard": {"value": wexamples.WORLD_POLL_LEADERBOARD_EXAMPLE}
    }
    leaderboard.operation_id = "listWorldPollLeaderboards"

    @action(
        detail=True,
        methods=["get"],
        serializer_class=URLWorldPollResourcesSerializer,
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

    resources.example = {"resources": {"value": wexamples.WORLD_POLL_RESOURCES_EXAMPLE}}
    resources.operation_id = "listWorldPollResources"
