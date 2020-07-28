from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from boundlexx.api.serializers import ColorSerializer
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.views.filters import LocalizationFilterSet
from boundlexx.api.views.mixins import DescriptiveAutoSchemaMixin
from boundlexx.boundless.models import Color

COLOR_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/colors/1/",
    "game_id": 1,
    "localization": [
        {"lang": "english", "name": "Black"},
        {"lang": "french", "name": "Noir"},
        {"lang": "german", "name": "Schwarz"},
        {"lang": "italian", "name": "Nero"},
        {"lang": "spanish", "name": "Negro"},
    ],
}


class ColorViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Color.objects.filter(active=True)
        .prefetch_related("localizedname_set")
        .order_by("game_id")
    )
    serializer_class = ColorSerializer
    lookup_field = "game_id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LocalizationFilterSet
    search_fields = ["game_id", "localizedname__name"]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(COLOR_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a color with a given ID
        """
        return super().retrieve(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"retrieve": {"value": COLOR_EXAMPLE}}  # type: ignore # noqa E501
