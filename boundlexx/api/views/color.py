from rest_framework import viewsets

from boundlexx.api.serializers import ColorSerializer
from boundlexx.api.views.mixins import DescriptiveAutoSchemaMixin
from boundlexx.boundless.models import Color

COLOR_EXAMPLE = {
    "id": 1,
    "localization": [
        {"lang": "english", "name": "Black"},
        {"lang": "french", "name": "Noir"},
        {"lang": "german", "name": "Schwarz"},
        {"lang": "italian", "name": "Nero"},
        {"lang": "spanish", "name": "Negro"},
    ],
}


class ColorViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Color.objects.filter(active=True).order_by("game_id")
    serializer_class = ColorSerializer
    lookup_field = "game_id"

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": [COLOR_EXAMPLE]}}  # type: ignore

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
