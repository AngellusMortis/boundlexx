from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.serializers import BlockColorSerializer, ColorSerializer
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.views.filters import LocalizationFilterSet
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
    "can_be_found": False,
    "new_color": None,
    "exist_via_transformation": None,
}


class ColorViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Color.objects.filter(active=True)
        .prefetch_related("localizedname_set", "colorvalue_set")
        .order_by("game_id")
    )
    serializer_class = ColorSerializer
    lookup_field = "game_id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LocalizationFilterSet
    search_fields = ["game_id", "localizedname__name"]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(COLOR_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a color with a given ID
        """
        return super().retrieve(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"retrieve": {"value": COLOR_EXAMPLE}}  # type: ignore # noqa E501


class BlockColorViewSet(
    NestedViewSetMixin, viewsets.ReadOnlyModelViewSet,
):
    schema = DescriptiveAutoSchema(tags=["Color"])
    queryset = WorldBlockColor.objects.select_related(
        "item", "world"
    ).order_by("item__game_id")

    serializer_class = BlockColorSerializer
    lookup_field = "item__game_id"

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of the items for a given color
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    list.example = {"list": {"value": get_list_example(COLOR_BLOCKS_EXAMPLE)}}  # type: ignore # noqa E501
    list.operation_id = "color-blocks"  # type: ignore # noqa E501

    def retrieve(
        self, request, *args, **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves the counts worlds for a given color/item combination
        """
        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    retrieve.example = {"list": {"value": get_list_example(COLOR_BLOCKS_EXAMPLE)}}  # type: ignore # noqa E501
    retrieve.operation_id = "color-blocks-item"  # type: ignore # noqa E501
