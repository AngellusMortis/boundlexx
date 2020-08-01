from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.serializers import (
    ItemColorSerializer,
    ItemResourceCountSerializer,
    ItemSerializer,
)
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.views.filters import LocalizationFilterSet
from boundlexx.api.views.mixins import DescriptiveAutoSchemaMixin
from boundlexx.boundless.models import Item, ResourceCount, WorldBlockColor

ITEM_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/items/9427/",
    "colors_url": f"{get_base_url()}/api/v1/items/9427/colors/",
    "game_id": 9427,
    "string_id": "ITEM_TYPE_SOIL_SILTY_COMPACT",
    "resource_counts_url": None,
    "localization": [
        {"lang": "english", "name": "Compact Silt"},
        {"lang": "french", "name": "Limon compact"},
        {"lang": "german", "name": "Kompaktierter Schluff"},
        {"lang": "italian", "name": "Sedimenti compatti"},
        {"lang": "spanish", "name": "Cieno compacto"},
    ],
    "item_subtitle": {
        "localization": [
            {"lang": "spanish", "name": "Bloque compacto común"},
            {"lang": "english", "name": "Common Compacted Block"},
            {"lang": "french", "name": "Bloc compacté commun"},
            {"lang": "german", "name": "Gewöhnlicher kompaktierter Block"},
            {"lang": "italian", "name": "Blocco compresso comune"},
        ]
    },
}

ITEM_RESOURCE_COUNT_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/items/10787/resource-counts/10/",
    "item_url": f"{get_base_url()}/api/v1/items/10787/",
    "world": {
        "url": f"{get_base_url()}/api/v1/worlds/10/",
        "id": 10,
        "display_name": "Serpensarindi",
    },
    "count": 100000,
}

ITEM_COLORS_EXAMPLE = {
    "color": {"url": f"{get_base_url()}/api/v1/colors/1/", "game_id": 1},
    "world": {"url": None, "id": 2000000075, "display_name": "Spination"},
}


class ItemViewSet(
    DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet,
):
    queryset = (
        Item.objects.filter(active=True)
        .select_related("item_subtitle")
        .prefetch_related(
            "localizedname_set",
            "item_subtitle__localizedname_set",
            "worldblockcolor_set",
        )
        .order_by("game_id")
    )
    serializer_class = ItemSerializer
    lookup_field = "game_id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LocalizationFilterSet
    search_fields = ["game_id", "string_id", "localizedname__name"]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of items avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(ITEM_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a items with a given ID.

        If a `resource_counts_url` is provided, it means this item is
        a "resource" in Boundless. `resource_counts_url` provide most
        resource counts of the item on all Boundless worlds.
        """
        return super().retrieve(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"retrieve": {"value": ITEM_EXAMPLE}}  # type: ignore # noqa E501


class ItemResourceCountViewSet(
    NestedViewSetMixin, viewsets.ReadOnlyModelViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Item"])
    queryset = (
        ResourceCount.objects.filter(
            world_poll__active=True, world_poll__world__active=True
        )
        .select_related("world_poll", "world_poll__world")
        .order_by("world_poll__world_id")
    )

    serializer_class = ItemResourceCountSerializer
    lookup_field = "world_id"
    filter_backends = [filters.SearchFilter]
    search_fields = ["world_poll__world__display_name"]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of the counts of the resource by world.

        This endpoint will only exist if the given item is a "resource"
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(ITEM_RESOURCE_COUNT_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the counts of the resource on a given world.
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

        if "item__game_id" in kwargs:
            try:
                game_id = int(kwargs["item__game_id"])
            except ValueError:
                pass
            else:
                if (
                    game_id
                    not in settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING
                ):
                    raise Http404()

        return kwargs


class ItemColorsViewSet(
    NestedViewSetMixin, viewsets.ReadOnlyModelViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Item"])
    queryset = WorldBlockColor.objects.select_related(
        "color", "world"
    ).order_by("color__game_id")

    serializer_class = ItemColorSerializer
    lookup_field = "color__game_id"

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors for a given item
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(ITEM_COLORS_EXAMPLE)}}  # type: ignore # noqa E501
    list.operation_id = "item-colors"  # type: ignore # noqa E501

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the list worlds for specific color/item combination
        """
        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"list": {"value": get_list_example(ITEM_COLORS_EXAMPLE)}}  # type: ignore # noqa E501
    retrieve.operation_id = "item-colors-color"  # type: ignore # noqa E501
