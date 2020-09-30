from typing import List

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.serializers import (
    BlockColorSerializer,
    ColorSerializer,
    PossibleItemSerializer,
)
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.views.filters import LocalizationFilterSet, WorldBlockColorFilterSet
from boundlexx.api.views.mixins import DescriptiveAutoSchemaMixin
from boundlexx.boundless.models import Color, WorldBlockColor

COLOR_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/colors/1/",
    "blocks_url": f"{get_base_url()}/api/v1/colors/1/blocks/",
    "game_id": 1,
    "base_color": "#1b1b1b",
    "gleam_color": "#1b1b1b",
    "localization": [
        {"lang": "english", "name": "Black"},
        {"lang": "french", "name": "Noir"},
        {"lang": "german", "name": "Schwarz"},
        {"lang": "italian", "name": "Nero"},
        {"lang": "spanish", "name": "Negro"},
    ],
}

COLOR_BLOCKS_EXAMPLE = {
    "item": {
        "url": f"{get_base_url()}/api/v1/items/13/?format=json",
        "game_id": 13,
        "string_id": "ITEM_TYPE_GRASS_VERDANT_BASE",
    },
    "world": {"url": None, "id": 2000000075, "display_name": "Spination"},
    "is_new_color": True,
    "exist_on_perm": True,
    "exist_via_transform": None,
}


class ColorViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Color.objects.filter(active=True).prefetch_related(
        "localizedname_set", "colorvalue_set"
    )
    serializer_class = ColorSerializer
    lookup_field = "game_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = LocalizationFilterSet
    search_fields = ["localizedname__name"]
    ordering = ["-rank", "game_id"]
    ordering_fields: List[str] = []

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(COLOR_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a color with a given ID
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": COLOR_EXAMPLE}}  # type: ignore # noqa E501

    @action(
        detail=True,
        methods=["get"],
        serializer_class=PossibleItemSerializer,
        url_path="sovereign-blocks",
    )
    def sovereign_blocks(
        self,
        request,
        game_id=None,
    ):
        """
        Gets current Possible Sovereign Blocks choices for given color
        """

        color = self.get_object()

        queryset = (
            WorldBlockColor.objects.filter(color=color, is_default=True)
            .filter(
                Q(world__isnull=True)
                | Q(world__end__isnull=True, world__is_creative=False)
                | Q(world__owner__isnull=False, world__is_creative=False)
            )
            .select_related("item")
            .order_by("item__game_id")
            .distinct("item__game_id")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class BlockColorViewSet(
    NestedViewSetMixin,
    viewsets.ReadOnlyModelViewSet,
):
    schema = DescriptiveAutoSchema()
    queryset = (
        WorldBlockColor.objects.filter(world__is_creative=False)
        .select_related(
            "item",
            "world",
            "item__item_subtitle",
        )
        .prefetch_related(
            "item__localizedname_set",
            "item__item_subtitle__localizedname_set",
        )
    )

    serializer_class = BlockColorSerializer
    lookup_field = "item__game_id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = WorldBlockColorFilterSet
    search_fields = [
        "item__string_id",
        "item__item_subtitle__localizedname__name",
        "item__localizedname__name",
        "world__name",
        "world__display_name",
    ]
    ordering = ["-rank", "item__game_id", "color__game_id"]
    ordering_fields: List[str] = []

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of the items for a given color
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(COLOR_BLOCKS_EXAMPLE)}}  # type: ignore # noqa E501
    list.operation_id = "color-blocks"  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the counts worlds for a given color/item combination
        """
        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"list": {"value": get_list_example(COLOR_BLOCKS_EXAMPLE)}}  # type: ignore # noqa E501
    retrieve.operation_id = "color-blocks-item"  # type: ignore # noqa E501
