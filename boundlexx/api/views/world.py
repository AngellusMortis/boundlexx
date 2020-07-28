from rest_framework import filters, viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.serializers import WorldPollSerializer, WorldSerializer
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.views.mixins import (
    DescriptiveAutoSchemaMixin,
    TimeseriesMixin,
)
from boundlexx.api.views.pagination import WorldPollPagination
from boundlexx.boundless.models import World, WorldPoll

WORLD_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/worlds/1/",
    "id": 251,
    "name": "aus3_t6_3",
    "display_name": "Typhuchis",
    "region": "aus",
    "tier": 6,
    "description": "WORLD_TYPE_RIFT",
    "size": 192,
    "world_type": "RIFT",
    "time_offset": "2020-07-14T12:01:11.160609Z",
    "is_sovereign": False,
    "is_perm": False,
    "is_creative": False,
    "is_locked": False,
    "is_public": True,
    "number_of_regions": 34,
    "start": "2020-07-26T21:40:35Z",
    "end": "2020-07-31T15:07:13Z",
    "atmosphere_color": "#b4d2ff",
    "water_color": "#c359ff",
}


class WorldViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    queryset = World.objects.filter(active=True).order_by("id")
    serializer_class = WorldSerializer
    lookup_field = "id"
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "id",
        "name",
        "display_name",
        "world_type",
        "tier",
        "region",
    ]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of worlds avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(WORLD_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a worlds with a given id
        """
        return super().retrieve(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"retrieve": {"value": WORLD_EXAMPLE}}  # type: ignore # noqa E501


class WorldPollViewSet(
    TimeseriesMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    schema = DescriptiveAutoSchema(tags=["World"])
    queryset = (
        WorldPoll.objects.filter(world__active=True)
        .prefetch_related(
            "worldpollresult_set",
            "leaderboardrecord_set",
            "resourcecount_set",
            "resourcecount_set__item",
        )
        .order_by("-time")
    )
    serializer_class = WorldPollSerializer
    lookup_field = "id"
    pagination_class = WorldPollPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
