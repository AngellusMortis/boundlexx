from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.serializers import ColorSerializer, ItemSerializer
from boundlexx.boundless.models import Color, Item


class DescriptiveAutoSchemaMixin:
    schema = DescriptiveAutoSchema()


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

ITEM_EXAMPLE = {
    "id": 9427,
    "string_id": "ITEM_TYPE_SOIL_SILTY_COMPACT",
    "localization": [
        {"lang": "english", "name": "Compact Silt"},
        {"lang": "french", "name": "Limon compact"},
        {"lang": "german", "name": "Kompaktierter Schluff"},
        {"lang": "italian", "name": "Sedimenti compatti"},
        {"lang": "spanish", "name": "Cieno compacto"},
    ],
}


class ColorViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Color.objects.filter(active=True).order_by("game_id")
    serializer_class = ColorSerializer

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list_colors": {"value": [COLOR_EXAMPLE]}}  # type: ignore

    def retrieve(self, request, pk=None):  # pylint: disable=arguments-differ
        """
        Retrieves a color with a given ID
        """
        color = get_object_or_404(self.get_queryset(), game_id=pk)
        serializer = self.get_serializer_class()(color)
        return Response(serializer.data)

    retrieve.example = {"retrieve_color": {"value": COLOR_EXAMPLE}}  # type: ignore # noqa E501


class ItemViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.filter(active=True).order_by("game_id")
    serializer_class = ItemSerializer

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of items avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list_items": {"value": [ITEM_EXAMPLE]}}  # type: ignore

    def retrieve(self, request, pk=None):  # pylint: disable=arguments-differ
        """
        Retrieves a items with a given ID
        """
        item = get_object_or_404(self.get_queryset(), game_id=pk)
        serializer = self.get_serializer_class()(item)
        return Response(serializer.data)

    retrieve.example = {"retrieve_item": {"value": ITEM_EXAMPLE}}  # type: ignore # noqa E501
