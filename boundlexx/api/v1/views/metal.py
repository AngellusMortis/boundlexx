from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter, LocalizationFilterSet
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.v1.serializers import URLMetalSerializer
from boundlexx.boundless.models import Metal

METAL_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/metal/0/",
    "game_id": 0,
    "localization": [
        {"lang": "english", "name": "Copper"},
        {"lang": "french", "name": "Cuivre"},
        {"lang": "german", "name": "Kupfer"},
        {"lang": "italian", "name": "Rame"},
        {"lang": "spanish", "name": "Cobre"},
    ],
}


class MetalViewSet(BoundlexxViewSet):
    queryset = Metal.objects.filter(active=True).prefetch_related("localizedname_set")
    serializer_class = URLMetalSerializer
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
    ordering_fields: list[str] = []

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of metals avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(METAL_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a metal with a given ID
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": METAL_EXAMPLE}}  # type: ignore # noqa E501
