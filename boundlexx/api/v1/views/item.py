from typing import List

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import (
    DedupedFilter,
    ItemColorFilterSet,
    ItemFilterSet,
    ItemResourceCountFilterSet,
)
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.v1.serializers import (
    PossibleColorSerializer,
    URLItemColorSerializer,
    URLItemRequestBasketPriceSerializer,
    URLItemResourceCountSerializer,
    URLItemSerializer,
    URLItemShopStandPriceSerializer,
    URLSimpleWorldSerializer,
    URLWorldColorSerializer,
)
from boundlexx.boundless.models import (
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
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

ITEM_REQUEST_BASKETS_EXAMPLE = {
    "time": "2020-08-30T15:30:27.593310-04:00",
    "location": {"x": 1358, "y": 67, "z": 1320},
    "world": {
        "url": f"{get_base_url()}/api/v1/worlds/23/",
        "id": 23,
        "display_name": "Dand",
    },
    "item_count": 14400,
    "price": "0.00",
    "beacon_name": "",
    "guild_tag": "",
    "shop_activity": 0,
}

ITEM_SHOP_STAND_EXAMPLE = {
    "time": "2020-08-30T15:30:30.037943-04:00",
    "location": {"x": 1493, "y": 73, "z": 644},
    "world": {
        "url": f"{get_base_url()}/api/v1/worlds/23/",
        "id": 23,
        "display_name": "Dand",
    },
    "item_count": 89,
    "price": "100.00",
    "beacon_name": "",
    "guild_tag": "",
    "shop_activity": 0,
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

ITEM_SOVEREIGN_COLORS_EXAMPLE = {
    "color": {"url": f"{get_base_url()}/api/v1/colors/1/", "game_id": 1}
}


class ItemViewSet(
    BoundlexxViewSet,
):
    queryset = (
        Item.objects.filter(active=True)
        .select_related("item_subtitle", "list_type", "description")
        .prefetch_related(
            "localizedname_set",
            "item_subtitle__localizedname_set",
            "worldblockcolor_set",
            "itembuyrank_set",
            "itemsellrank_set",
            "list_type__strings",
            "description__strings",
        )
    )
    serializer_class = URLItemSerializer
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

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of items avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

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
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": ITEM_EXAMPLE}}  # type: ignore # noqa E501

    @action(
        detail=True,
        methods=["get"],
        serializer_class=URLItemShopStandPriceSerializer,
        url_path="shop-stands",
    )
    def shop_stands(
        self,
        request,
        game_id=None,
    ):
        """
        Gets current Shop Stands for given item
        """

        item = self.get_object()

        queryset = ItemShopStandPrice.objects.filter(item=item, active=True).order_by(
            "world_id"
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    shop_stands.example = {
        "shop_stands": {"value": get_list_example(ITEM_SHOP_STAND_EXAMPLE)}
    }
    shop_stands.operation_id = "listItemShopStands"  # noqa E501

    @action(
        detail=True,
        methods=["get"],
        serializer_class=URLItemRequestBasketPriceSerializer,
        url_path="request-baskets",
    )
    def request_baskets(
        self,
        request,
        game_id=None,
    ):
        """
        Gets current Request Baskets for given item
        """

        item = self.get_object()

        queryset = ItemRequestBasketPrice.objects.filter(
            item=item, active=True
        ).order_by("world_id")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    request_baskets.example = {
        "request_baskets": {"value": get_list_example(ITEM_REQUEST_BASKETS_EXAMPLE)}
    }
    request_baskets.operation_id = "listItemRequestBaskets"  # noqa E501

    @action(
        detail=True,
        methods=["get"],
        serializer_class=PossibleColorSerializer,
        url_path="sovereign-colors",
    )
    def sovereign_colors(
        self,
        request,
        game_id=None,
    ):
        """
        Gets current Possible Sovereign Color choices for given item
        """

        item = self.get_object()

        queryset = (
            WorldBlockColor.objects.filter(item=item, is_default=True)
            .filter(
                Q(world__isnull=True)
                | Q(world__end__isnull=True, world__is_creative=False)
                | Q(world__owner__isnull=False, world__is_creative=False)
            )
            .select_related("color")
            .order_by("color__game_id")
            .distinct("color__game_id")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    sovereign_colors.example = {
        "sovereign_colors": {"value": get_list_example(ITEM_SOVEREIGN_COLORS_EXAMPLE)}
    }
    sovereign_colors.operation_id = "listItemSovereignColors"  # noqa E501


class ItemResourceWorldListViewSet(
    NestedViewSetMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    schema = DescriptiveAutoSchema(tags=["Items"])
    serializer_class = URLSimpleWorldSerializer

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

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(ITEM_RESOURCES_WORLD_LIST_EXAMPLE)}}  # type: ignore # noqa E501
    list.operation_id = "listItemResourceWorlds"  # type: ignore # noqa E501


class ItemResourceCountViewSet(
    NestedViewSetMixin,
    BoundlexxViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Items"])
    queryset = ResourceCount.objects.filter(
        world_poll__active=True, world_poll__world__active=True
    ).select_related("world_poll", "world_poll__world", "item")

    serializer_class = URLItemResourceCountSerializer
    lookup_field = "world_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = ItemResourceCountFilterSet
    search_fields = [
        "world_poll__world__display_name",
        "world_poll__world__name",
    ]
    ordering = ["-rank", "world_poll__world_id", "-count"]
    ordering_fields: List[str] = [
        "count",
        "average_per_chunk",
        "percentage",
    ]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of the counts of the resource by world.

        This endpoint will only exist if the given item is a "resource"
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(ITEM_RESOURCE_COUNT_EXAMPLE)}}  # type: ignore # noqa E501
    list.operation_id = "listItemResourceCounts"  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the counts of the resource on a given world.
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": ITEM_RESOURCE_COUNT_EXAMPLE}}  # type: ignore # noqa E501
    retrieve.operation_id = "retrieveItemResourceCount"  # type: ignore # noqa E501

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
                if game_id not in settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING:
                    raise Http404()

        return kwargs


class ItemColorsViewSet(
    NestedViewSetMixin,
    BoundlexxViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Items"])
    queryset = (
        WorldBlockColor.objects.filter(world__is_creative=False)
        .select_related(
            "color",
            "world",
            "item",
        )
        .prefetch_related("color__localizedname_set")
    )
    lookup_field = "color__game_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = ItemColorFilterSet
    search_fields = [
        "color__localizedname__name",
    ]
    ordering = ["-rank", "color__game_id", "world_id"]
    ordering_fields: List[str] = []

    serializer_class = URLItemColorSerializer
    detail_serializer_class = URLWorldColorSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            queryset = queryset.distinct("rank", "color__game_id")

        return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors for a given item
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(ITEM_COLORS_EXAMPLE)}}  # type: ignore # noqa E501
    list.operation_id = "listItemColors"  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the list worlds for specific color/item combination
        """
        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"list": {"value": get_list_example(ITEM_COLORS_EXAMPLE)}}  # type: ignore # noqa E501
    retrieve.operation_id = "retrieveItemColors"  # type: ignore # noqa E501
