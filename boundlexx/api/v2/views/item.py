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
from boundlexx.api.common.serializers import (
    IDWorldSerializer,
    ItemColorSerializer,
    ItemRequestBasketPriceSerializer,
    ItemResourceCountSerializer,
    ItemSerializer,
    ItemShopStandPriceSerializer,
    PossibleWBCSerializer,
    SimpleItemSerializer,
    WorldColorSerializer,
)
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.boundless.models import (
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    ResourceCount,
    World,
    WorldBlockColor,
)


class ItemViewSet(
    BoundlexxViewSet,
):
    queryset = (
        Item.objects.filter(active=True)
        .select_related("item_subtitle", "list_type", "description")
        .prefetch_related(
            "localizedname_set",
            "item_subtitle__localizedname_set",
            "list_type__strings",
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

    @action(
        detail=True,
        methods=["get"],
        serializer_class=ItemShopStandPriceSerializer,
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

        queryset = (
            ItemShopStandPrice.objects.filter(item=item, active=True)
            .select_related("world")
            .order_by("price")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    shop_stands.operation_id = "listItemShopStands"  # noqa E501

    @action(
        detail=True,
        methods=["get"],
        serializer_class=ItemRequestBasketPriceSerializer,
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

        queryset = (
            ItemRequestBasketPrice.objects.filter(item=item, active=True)
            .select_related("world")
            .order_by("-price")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    request_baskets.operation_id = "listItemRequestBaskets"  # noqa E501

    @action(
        detail=True,
        methods=["get"],
        serializer_class=PossibleWBCSerializer,
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

    sovereign_colors.operation_id = "listItemSovereignColors"  # noqa E501


class ItemResourceCountViewSet(
    NestedViewSetMixin,
    BoundlexxViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Items"])
    queryset = ResourceCount.objects.filter(
        world_poll__active=True,
        world_poll__world__active=True,
        world_poll__world__is_public=True,
        world_poll__world__is_creative=False,
    ).select_related("world_poll", "world_poll__world", "item", "item__resource_data")

    serializer_class = ItemResourceCountSerializer
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
        WorldBlockColor.objects.filter(world__is_creative=False, world__is_public=True)
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

    serializer_class = ItemColorSerializer
    detail_serializer_class = WorldColorSerializer

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

    retrieve.operation_id = "retrieveItemColors"  # type: ignore # noqa E501


class ItemResourceWorldListViewSet(
    NestedViewSetMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    schema = DescriptiveAutoSchema(tags=["Items"])
    serializer_class = IDWorldSerializer

    def get_queryset(self):
        item_id = self.kwargs.get("item__game_id")

        if item_id not in settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING:
            raise Http404

        queryset = World.objects.filter(is_public=True)

        if item_id is not None:
            queryset = queryset.filter(
                worldpoll__resourcecount__item__game_id=item_id
            ).distinct("id")

        return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of worlds that has this resource on item
        timeseries lookup
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.operation_id = "listItemResourceWorlds"  # type: ignore # noqa E501
