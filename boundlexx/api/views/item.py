from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.serializers import (
    ItemResourceCountSerializer,
    ItemSerializer,
)
from boundlexx.api.views.mixins import DescriptiveAutoSchemaMixin
from boundlexx.boundless.models import Item, ResourceCount

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

ITEM_RESOURCE_COUNT_EXAMPLE = {
    "world": {"id": 10, "display_name": "Serpensarindi"},
    "count": 100000,
}


class ItemViewSet(
    DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet,
):
    queryset = Item.objects.filter(active=True).order_by("game_id")
    serializer_class = ItemSerializer
    lookup_field = "game_id"

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of items avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": [ITEM_EXAMPLE]}}  # type: ignore

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a items with a given ID
        """
        return super().retrieve(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"retrieve": {"value": ITEM_EXAMPLE}}  # type: ignore # noqa E501


class ItemResourceCountViewSet(
    NestedViewSetMixin, viewsets.ReadOnlyModelViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Item"])
    queryset = ResourceCount.objects.filter(world_poll__active=True).order_by(
        "world_poll__world_id"
    )
    serializer_class = ItemResourceCountSerializer
    lookup_field = "world_id"

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of the counts of the resource by world
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": [ITEM_RESOURCE_COUNT_EXAMPLE]}}  # type: ignore # noqa E501

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the counts of the resource on a given world
        """
        return super().retrieve(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"retrieve": {"value": ITEM_RESOURCE_COUNT_EXAMPLE}}  # type: ignore # noqa E501

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(
            queryset, world_poll__world_id=self.kwargs[self.lookup_field]
        )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_parents_query_dict(self):
        kwargs = super().get_parents_query_dict()
        kwargs.pop(self.lookup_field, None)

        return kwargs
