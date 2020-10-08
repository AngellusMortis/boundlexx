from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter, WorldFilterSet
from boundlexx.api.common.serializers import SimpleWorldSerializer, WorldSerializer
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.boundless.models import World


class WorldViewSet(BoundlexxViewSet):
    queryset = World.objects.all()
    serializer_class = SimpleWorldSerializer
    detail_serializer_class = WorldSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = WorldFilterSet
    ordering = ["-rank", "id"]
    ordering_fields: List[str] = ["sort_name", "start", "end"]
    search_fields = [
        "name",
        "id",
        "text_name",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        # only get all relations on detail view
        if self.detail:
            queryset = queryset.select_related("assignment").prefetch_related(
                "worldblockcolor_set",
                "worldblockcolor_set__item",
                "worldblockcolor_set__color",
                "worldblockcolor_set__first_world",
                "worldblockcolor_set__last_exo",
                "worldblockcolor_set__transform_first_world",
                "worldblockcolor_set__transform_last_exo",
                "itembuyrank_set",
                "itemsellrank_set",
            )

        return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of worlds avaiable in Boundless.

        This endpoint is deprecated in favor of `/api/v1/worlds/simple/`.

        The functionality of this endpoint will be replaced with that one in the
        on 1 December 2020.
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a worlds with a given id
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member
