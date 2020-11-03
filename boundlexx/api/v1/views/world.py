from collections import namedtuple
from logging import getLogger
from typing import List

from django.db.models import Q
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter, WorldFilterSet
from boundlexx.api.common.serializers import BeaconSerializer
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.examples import world as examples
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.utils import get_list_example
from boundlexx.api.v1.serializers import (
    KindOfSimpleWorldSerializer,
    URLWorldDistanceSerializer,
    URLWorldRequestBasketPriceSerializer,
    URLWorldSerializer,
    URLWorldShopStandPriceSerializer,
    WorldBlockColorsViewSerializer,
)
from boundlexx.boundless.models import (
    Beacon,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    World,
    WorldDistance,
)

BlockColorResponse = namedtuple("BlockColorResponse", ("id", "block_colors"))

logger = getLogger(__file__)


class WorldViewSet(BoundlexxViewSet):
    queryset = (
        World.objects.filter(is_public=True)
        .select_related("assignment")
        .prefetch_related(
            "worldblockcolor_set",
            "worldblockcolor_set__item",
            "worldblockcolor_set__color",
            "worldblockcolor_set__first_world",
            "worldblockcolor_set__last_exo",
            "worldblockcolor_set__transform_first_world",
            "worldblockcolor_set__transform_last_exo",
            "itembuyrank_set",
            "itemsellrank_set",
        )
    )
    serializer_class = URLWorldSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = WorldFilterSet
    ordering = ["-rank", "id"]
    ordering_fields: List[str] = ["sort_name", "start", "end"]
    search_fields = [
        "name",
        "id",
        "text_name",
    ]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of worlds avaiable in Boundless.

        This endpoint is deprecated in favor of `/api/v1/worlds/simple/`.

        The functionality of this endpoint will be replaced with that one in the
        on 1 December 2020.
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(examples.WORLD_EXAMPLE)}}  # type: ignore # noqa E501
    list.deprecated = True  # type: ignore

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a worlds with a given id
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": examples.WORLD_EXAMPLE}}  # type: ignore # noqa E501

    @action(
        detail=False,
        methods=["get"],
        serializer_class=KindOfSimpleWorldSerializer,
        url_path="simple",
    )
    def simple(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    simple.operation_id = "listWorldsSimple"

    @action(
        detail=True,
        methods=["get"],
        serializer_class=WorldBlockColorsViewSerializer,
        url_path="block-colors",
    )
    def block_colors(
        self,
        request,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Retrieves the block colors for a given world
        """

        world = self.get_object()

        show_inactive_colors = request.query_params.get("show_inactive_colors", False)
        is_default = request.query_params.get("is_default", None)

        all_block_colors = list(world.worldblockcolor_set.all())

        block_colors = []
        for bc in all_block_colors:
            if is_default is not None:
                if is_default and not bc.is_default:
                    continue
                if not is_default and bc.is_default:
                    continue

            if show_inactive_colors or bc.active:
                block_colors.append(bc)

        response = BlockColorResponse(world.id, block_colors)

        serializer = self.get_serializer_class()(response, context={"request": request})

        return Response(serializer.data)

    block_colors.example = {"block_colors": {"value": examples.WORLD_COLORS_EXAMPLE}}
    block_colors.operation_id = "listWorldBlockColors"

    @action(
        detail=True,
        methods=["get"],
        serializer_class=URLWorldShopStandPriceSerializer,
        url_path="shop-stands",
    )
    def shop_stands(
        self,
        request,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Gets current Shop Stands for given world
        """

        world = self.get_object()

        queryset = (
            ItemShopStandPrice.objects.filter(world=world, active=True)
            .select_related("item")
            .order_by("item_id", "price")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    shop_stands.example = {
        "shop_stands": {"value": get_list_example(examples.WORLD_SHOP_STANDS_EXAMPLE)}
    }
    shop_stands.operation_id = "listWorldShopStands"

    @action(
        detail=True,
        methods=["get"],
        serializer_class=URLWorldRequestBasketPriceSerializer,
        url_path="request-baskets",
    )
    def request_baskets(
        self,
        request,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Gets current Request Baskets for given world
        """

        world = self.get_object()

        queryset = (
            ItemRequestBasketPrice.objects.filter(world=world, active=True)
            .select_related("item")
            .order_by("item_id", "-price")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    request_baskets.example = {
        "request_baskets": {
            "value": get_list_example(examples.WORLD_REQUEST_BASKETS_EXAMPLE)
        }
    }
    request_baskets.operation_id = "listWorldRequestBaskets"

    @action(
        detail=True,
        methods=["get"],
        serializer_class=BeaconSerializer,
        url_path="beacons",
    )
    def beacons(
        self,
        request,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Gets current Beacons for given world
        """

        world = self.get_object()

        queryset = (
            Beacon.objects.filter(world=world, active=True)
            .prefetch_related("beaconscan_set", "beaconplotcolumn_set")
            .order_by("location_x", "location_y", "location_z")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    beacons.operation_id = "listWorldBeacons"


class WorldDistanceViewSet(NestedViewSetMixin, BoundlexxViewSet):
    queryset = (
        WorldDistance.objects.filter(world_source__active=True, world_dest__active=True)
        .select_related("world_source", "world_dest")
        .order_by("distance")
    )
    schema = DescriptiveAutoSchema(tags=["Worlds"])
    serializer_class = URLWorldDistanceSerializer
    lookup_field = "world_id"

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_field = self.lookup_url_kwarg or self.lookup_field
        world_id = self.kwargs[lookup_field]
        source_world_id = self.kwargs.get("world_source__id", None)

        if world_id == source_world_id:
            queryset = queryset.filter(
                world_source__id=world_id, world_dest__id=world_id
            )
        else:
            queryset = queryset.filter(
                Q(world_source__id=world_id) | Q(world_dest__id=world_id)
            )

        if queryset.count() > 1:
            logger.warning(
                "Duplicate World Distance calculations! %s %s",
                world_id,
                source_world_id,
            )

        obj = queryset.first()

        if obj is None:
            raise Http404

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()

        world_id = parents_query_dict.pop("world_source__id", None)
        if world_id:
            try:
                return queryset.filter(
                    Q(world_source__id=world_id) | Q(world_dest__id=world_id)
                )
            except ValueError as ex:
                raise Http404 from ex
        else:
            return queryset

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of distances to know worlds
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(examples.WORLD_DISTANCES_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the distance to a specific world
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": examples.WORLD_DISTANCES_EXAMPLE}}  # type: ignore # noqa E501
