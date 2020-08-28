from typing import List

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.serializers import (
    ItemColorSerializer,
    ItemResourceCountSerializer,
    ItemResourceCountTimeSeriesSerializer,
    ItemResourceCountTimeSeriesTBSerializer,
    ItemSerializer,
    SimpleWorldSerializer,
)
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.views.filters import (
    ItemColorFilterSet,
    ItemResourceCountFilterSet,
    LocalizationFilterSet,
)
from boundlexx.api.views.mixins import (
    DescriptiveAutoSchemaMixin,
    TimeseriesMixin,
)
from boundlexx.boundless.models import (
    Item,
    ResourceCount,
    World,
    WorldBlockColor,
)

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
    "is_new_color": True,
    "exist_on_perm": True,
    "exist_via_transform": None,
}

ITEM_RESOURCES_WORLD_LIST_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/worlds/1/",
    "id": 1,
    "display_name": "Sochaltin I",
}


ITEM_RESOURCE_TIMESERIES_EXAMPLE = {
    "time": "2020-08-04T09:09:50.136765-04:00",
    "url": f"{get_base_url()}/api/v1/items/32779/resource-counts/1/",
    "item_url": f"{get_base_url()}/api/v1/items/32779/",
    "world": {
        "url": f"{get_base_url()}/api/v1/worlds/1/",
        "id": 1,
        "display_name": "Sochaltin I",
    },
    "count": 6051899,
}


class ItemViewSet(
    DescriptiveAutoSchemaMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = (
        Item.objects.filter(active=True)
        .select_related("item_subtitle")
        .prefetch_related(
            "localizedname_set",
            "item_subtitle__localizedname_set",
            "worldblockcolor_set",
        )
    )
    serializer_class = ItemSerializer
    lookup_field = "game_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = LocalizationFilterSet
    search_fields = ["string_id", "localizedname__name"]
    ordering = ["-rank", "game_id"]
    ordering_fields: List[str] = []

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of items avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(ITEM_EXAMPLE)}}  # type: ignore # noqa E501

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
        return super().retrieve(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"retrieve": {"value": ITEM_EXAMPLE}}  # type: ignore # noqa E501


class ItemResourceTimeseriesViewSet(
    TimeseriesMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    schema = DescriptiveAutoSchema(tags=["Item"])
    queryset = ResourceCount.objects.filter(world_poll__world__active=True)
    serializer_class = ItemResourceCountTimeSeriesSerializer
    time_bucket_serializer_class = ItemResourceCountTimeSeriesTBSerializer
    number_fields = ["count"]
    lookup_field = "id"

    def get_queryset(self):
        queryset = super().get_queryset()

        if queryset.count() == 0:
            raise Http404

        return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list resource counts for a give item/world combination
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(ITEM_RESOURCE_TIMESERIES_EXAMPLE)}}  # type: ignore # noqa E501
    list.operation_id = "list-item-resource-timeseries"  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a specific resource counts for a give item/world combination
        """
        return super().retrieve(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"retrieve": {"value": ITEM_RESOURCE_TIMESERIES_EXAMPLE}}  # type: ignore # noqa E501


class ItemResourceWorldListViewSet(
    NestedViewSetMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    schema = DescriptiveAutoSchema(tags=["Item"])
    serializer_class = SimpleWorldSerializer

    def get_queryset(self):
        item_id = self.kwargs.get("item__game_id")

        queryset = World.objects.all()

        if item_id is not None:
            queryset = queryset.filter(
                worldpoll__resourcecount__item__game_id=item_id
            ).distinct("id")

        if queryset.count() == 0:
            raise Http404

        return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of worlds that has this resource on item
        timeseries lookup
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(ITEM_RESOURCES_WORLD_LIST_EXAMPLE)}}  # type: ignore # noqa E501


class ItemResourceCountViewSet(
    NestedViewSetMixin,
    viewsets.ReadOnlyModelViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Item"])
    queryset = ResourceCount.objects.filter(
        world_poll__active=True, world_poll__world__active=True
    ).select_related("world_poll", "world_poll__world")

    serializer_class = ItemResourceCountSerializer
    lookup_field = "world_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ItemResourceCountFilterSet
    search_fields = [
        "world_poll__world__display_name",
        "world_poll__world__name",
    ]
    ordering = ["-rank", "world_poll__world_id"]
    ordering_fields: List[str] = []

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
        self,
        request,
        *args,
        **kwargs,
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
    NestedViewSetMixin,
    viewsets.ReadOnlyModelViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Item"])
    queryset = WorldBlockColor.objects.select_related(
        "color",
        "world",
        "item",
    ).prefetch_related("color__localizedname_set")
    serializer_class = ItemColorSerializer
    lookup_field = "color__game_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ItemColorFilterSet
    search_fields = [
        "color__localizedname__name",
        "world__display_name",
        "world__name",
    ]
    ordering = ["-rank", "color__game_id"]
    ordering_fields: List[str] = []

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
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the list worlds for specific color/item combination
        """
        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"list": {"value": get_list_example(ITEM_COLORS_EXAMPLE)}}  # type: ignore # noqa E501
    retrieve.operation_id = "item-colors-color"  # type: ignore # noqa E501
