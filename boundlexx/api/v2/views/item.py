from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter, ItemFilterSet
from boundlexx.api.common.mixins import DescriptiveAutoSchemaMixin
from boundlexx.api.common.serializers import ItemSerializer, SimpleItemSerializer
from boundlexx.boundless.models import Item


class ItemViewSet(
    DescriptiveAutoSchemaMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = (
        Item.objects.filter(active=True)
        .select_related("item_subtitle", "list_type", "description")
        .prefetch_related(
            "localizedname_set",
        )
    )
    serializer_class = SimpleItemSerializer
    detail_serializer_class = ItemSerializer
    lookup_field = "game_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = ItemFilterSet
    search_fields = ["string_id", "localizedname__name", "game_id"]
    ordering = ["-rank", "game_id"]
    ordering_fields: List[str] = []

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.detail_serializer_class

        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()

        # only get all relations on detail view
        if self.detail:
            queryset = queryset.prefetch_related(
                "item_subtitle__localizedname_set",
                "worldblockcolor_set",
                "itembuyrank_set",
                "itemsellrank_set",
                "list_type__strings",
                "description__strings",
            )

        return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of items avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a items with a given ID.

        If a `resource_counts_url` is provided, it means this item is
        a "resource" in Boundless. `resource_counts_url` provide most
        resource counts of the item on all Boundless worlds.
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member
