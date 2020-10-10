from collections import namedtuple
from logging import getLogger
from typing import List

from django.db.models import Prefetch, Q
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_msgpack.renderers import MessagePackRenderer
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter, WorldFilterSet
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
    WorldDumpSerializer,
)
from boundlexx.boundless.models import (
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    World,
    WorldBlockColor,
    WorldDistance,
    WorldPoll,
)

BlockColorResponse = namedtuple("BlockColorResponse", ("id", "block_colors"))

logger = getLogger(__file__)


class WorldViewSet(BoundlexxViewSet):
    queryset = (
        World.objects.all()
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

        all_block_colors = list(world.worldblockcolor_set.all())

        block_colors = []
        for bc in all_block_colors:
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

        queryset = ItemShopStandPrice.objects.filter(world=world, active=True).order_by(
            "item_id"
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

        queryset = ItemRequestBasketPrice.objects.filter(
            world=world, active=True
        ).order_by("item_id")

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

    @method_decorator(cache_page(3600))
    @action(
        detail=False,
        methods=["get"],
        serializer_class=WorldDumpSerializer,
        url_path="dump",
        renderer_classes=[MessagePackRenderer],
    )
    def dump(
        self,
        request,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Returns all details about a world in a single request. Cached for 60
        minutes. Only supports `msgpack` format and not support `json` or `api.
        """

        queryset = World.objects.all().prefetch_related(
            Prefetch(
                "worldblockcolor_set",
                queryset=WorldBlockColor.objects.filter(active=True)
                .order_by("world_id", "item__game_id", "-time")
                .distinct("world_id", "item__game_id"),
                to_attr="active_colors",
            ),
            Prefetch(
                "worldpoll_set",
                queryset=WorldPoll.objects.filter(active=True)
                .order_by("world_id", "-time")
                .distinct("world_id"),
                to_attr="latest_poll",
            ),
            "latest_poll__resourcecount_set",
            "latest_poll__leaderboardrecord_set",
            "latest_poll__resourcecount_set__item",
            "latest_poll__resourcecount_set__world_poll",
            "active_colors__color",
            "active_colors__item",
            "active_colors__world",
            "active_colors__first_world",
            "active_colors__last_exo",
            "active_colors__transform_first_world",
            "active_colors__transform_last_exo",
        )
        serializer = self.get_serializer(queryset, many=True)

        response = Response(serializer.data)
        return response

    dump.operation_id = "dumpWorlds"


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
