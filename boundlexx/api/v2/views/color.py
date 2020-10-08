from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter, LocalizationFilterSet
from boundlexx.api.common.serializers import ColorSerializer
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.boundless.models import Color


class ColorViewSet(BoundlexxViewSet):
    queryset = Color.objects.filter(active=True).prefetch_related(
        "localizedname_set", "colorvalue_set"
    )
    serializer_class = ColorSerializer
    lookup_field = "game_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = LocalizationFilterSet
    search_fields = ["localizedname__name", "game_id"]
    ordering = ["-rank", "game_id"]
    ordering_fields: List[str] = []

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a color with a given ID
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member
