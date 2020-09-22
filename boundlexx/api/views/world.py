from collections import namedtuple
from typing import List

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.examples import world as examples
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.serializers import (
    SimpleWorldRequestBasketPriceSerializer,
    SimpleWorldShopStandPriceSerializer,
    WorldBlockColorsViewSerializer,
    WorldDistanceSerializer,
    WorldPollLeaderboardSerializer,
    WorldPollResourcesSerializer,
    WorldPollSerializer,
    WorldPollTBSerializer,
    WorldSerializer,
)
from boundlexx.api.utils import get_list_example
from boundlexx.api.views.filters import WorldFilterSet
from boundlexx.api.views.mixins import DescriptiveAutoSchemaMixin, TimeseriesMixin
from boundlexx.boundless.models import (
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    World,
    WorldDistance,
    WorldPoll,
)

BlockColorResponse = namedtuple("BlockColorResponse", ("id", "block_colors"))


class WorldViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
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
    serializer_class = WorldSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = WorldFilterSet
    ordering = ["-rank", "id"]
    ordering_fields: List[str] = ["display_name"]
    search_fields = [
        "name",
        "display_name",
    ]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of worlds avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(examples.WORLD_EXAMPLE)}}  # type: ignore # noqa E501

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

    @action(
        detail=True,
        methods=["get"],
        serializer_class=SimpleWorldShopStandPriceSerializer,
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

    @action(
        detail=True,
        methods=["get"],
        serializer_class=SimpleWorldRequestBasketPriceSerializer,
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

    request_baskets.example = {
        "request_baskets": {
            "value": get_list_example(examples.WORLD_REQUEST_BASKETS_EXAMPLE)
        }
    }


class WorldPollViewSet(
    TimeseriesMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    schema = DescriptiveAutoSchema(tags=["World"])
    queryset = WorldPoll.objects.all().prefetch_related(
        "worldpollresult_set",
        "leaderboardrecord_set",
        "resourcecount_set",
        "resourcecount_set__item",
    )
    serializer_class = WorldPollSerializer
    time_bucket_serializer_class = WorldPollTBSerializer
    number_fields = [
        "worldpollresult__player_count",
        "worldpollresult__beacon_count",
        "worldpollresult__plot_count",
        "worldpollresult__total_prestige",
    ]
    lookup_field = "id"

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list polls avaiable for give World
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(examples.WORLD_POLL_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a specific poll for a given world

        Can pass `latest` in place of `id` to retrieve the newsest one
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": examples.WORLD_POLL_EXAMPLE}}  # type: ignore # noqa E501

    @action(
        detail=True,
        methods=["get"],
        serializer_class=WorldPollLeaderboardSerializer,
    )
    def leaderboard(
        self,
        request,
        world_id=None,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Retrieves the leaderboard for a given world poll result
        """

        world_poll = self.get_object()

        serializer = self.get_serializer_class()(
            world_poll, context={"request": request}
        )

        return Response(serializer.data)

    leaderboard.example = {
        "leaderboard": {"value": examples.WORLD_POLL_LEADERBOARD_EXAMPLE}
    }

    @action(
        detail=True,
        methods=["get"],
        serializer_class=WorldPollResourcesSerializer,
    )
    def resources(
        self,
        request,
        world_id=None,
        id=None,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Retrieves the count of resources for a given world poll result
        """
        world_poll = self.get_object()

        serializer = self.get_serializer_class()(
            world_poll, context={"request": request}
        )

        return Response(
            {
                "world_poll_id": id,
                "world_poll_url": reverse(
                    "world-poll-detail",
                    kwargs={"world_id": world_id, "id": id},
                    request=request,
                ),
                "resources": serializer.data,
            }
        )

    resources.example = {
        "leaderboard": {"value": examples.WORLD_POLL_RESOURCES_EXAMPLE}
    }


class WorldDistanceViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        WorldDistance.objects.filter(world_source__active=True, world_dest__active=True)
        .select_related("world_source", "world_dest")
        .order_by("distance")
    )
    schema = DescriptiveAutoSchema(tags=["World"])
    serializer_class = WorldDistanceSerializer
    lookup_field = "world_id"

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_field = self.lookup_url_kwarg or self.lookup_field
        world_id = self.kwargs[lookup_field]
        source_world_id = self.kwargs.get("world_source__id", None)

        if world_id == source_world_id:
            obj = get_object_or_404(
                queryset, world_source__id=world_id, world_dest__id=world_id
            )
        else:
            obj = get_object_or_404(
                queryset,
                Q(world_source__id=world_id) | Q(world_dest__id=world_id),
            )

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
