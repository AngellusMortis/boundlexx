from django_filters.rest_framework import DjangoFilterBackend

from boundlexx.api.common.filters import LocalizationFilterSet
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.v1.serializers import RecipeGroupSerializer, RecipeSerializer
from boundlexx.api.v1.views.filters import RecipeFilterSet
from boundlexx.boundless.models import Recipe, RecipeGroup

RECIPE_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/recipes/1616/",
    "id": 1616,
    "heat": 0,
    "craft_xp": 16,
    "machine": "REFINERY",
    "output": {
        "url": f"{get_base_url()}/api/v1/items/9635/",
        "game_id": 9635,
        "name": "METAL_GOLD_REFINED",
        "string_id": "ITEM_TYPE_METAL_GOLD_REFINED",
    },
    "can_hand_craft": False,
    "machine_level": "Powered",
    "power": 0,
    "group_name": "UNDEFINED",
    "knowledge_unlock_level": 15,
    "tints": [],
    "requirements": [],
    "levels": [
        {
            "level": 0,
            "wear": 35,
            "spark": 400,
            "duration": 50,
            "output_quantity": 1,
            "inputs": [
                {
                    "group": None,
                    "item": {
                        "url": f"{get_base_url()}/api/v1/items/9615/",
                        "game_id": 9615,
                        "name": "METAL_GOLD_COMPACT",
                        "string_id": "ITEM_TYPE_METAL_GOLD_COMPACT",
                    },
                }
            ],
        },
        {
            "level": 1,
            "wear": 160,
            "spark": 4000,
            "duration": 500,
            "output_quantity": 10,
            "inputs": [
                {
                    "group": None,
                    "item": {
                        "url": f"{get_base_url()}/api/v1/items/9615/",
                        "game_id": 9615,
                        "name": "METAL_GOLD_COMPACT",
                        "string_id": "ITEM_TYPE_METAL_GOLD_COMPACT",
                    },
                }
            ],
        },
        {
            "level": 2,
            "wear": 520,
            "spark": 20000,
            "duration": 2500,
            "output_quantity": 50,
            "inputs": [
                {
                    "group": None,
                    "item": {
                        "url": f"{get_base_url()}/api/v1/items/9615/",
                        "game_id": 9615,
                        "name": "METAL_GOLD_COMPACT",
                        "string_id": "ITEM_TYPE_METAL_GOLD_COMPACT",
                    },
                }
            ],
        },
    ],
    "required_event": None,
    "required_backer_tier": None,
}

RECIPE_GROUP_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/recipe-groups/1/",
    "id": 1,
    "name": "Any Soil",
    "display_name": {
        "string_id": "ITEM_ANY_SOIL",
        "strings": [
            {
                "lang": "spanish",
                "text": "Cualquier Tierra",
                "plain_text": "Cualquier Tierra",
            },
            {
                "lang": "german",
                "text": "Irgendein Boden",
                "plain_text": "Irgendein Boden",
            },
            {"lang": "english", "text": "Any Soil", "plain_text": "Any Soil"},
            {
                "lang": "french",
                "text": "N'importe quel sol",
                "plain_text": "N'importe quel sol",
            },
            {
                "lang": "italian",
                "text": "Qualsiasi suolo",
                "plain_text": "Qualsiasi suolo",
            },
        ],
    },
    "members": [
        {
            "url": f"{get_base_url()}/api/v1/items/11584/",
            "game_id": 11584,
            "name": "SOIL_SILTY_BASE_DUGUP",
            "string_id": "ITEM_TYPE_SOIL_SILTY_BASE",
        },
        {
            "url": f"{get_base_url()}/api/v1/items/11588/",
            "game_id": 11588,
            "name": "SOIL_CLAY_BASE_DUGUP",
            "string_id": "ITEM_TYPE_SOIL_CLAY_BASE",
        },
        {
            "url": f"{get_base_url()}/api/v1/items/11592/",
            "game_id": 11592,
            "name": "SOIL_PEATY_BASE_DUGUP",
            "string_id": "ITEM_TYPE_SOIL_PEATY_BASE",
        },
    ],
}


class RecipeGroupViewSet(BoundlexxViewSet):
    schema = DescriptiveAutoSchema(tags=["Skills"])

    queryset = (
        RecipeGroup.objects.all()
        .select_related("display_name")
        .prefetch_related("members", "display_name__strings")
    )
    serializer_class = RecipeGroupSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = LocalizationFilterSet

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of skill groups avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(RECIPE_GROUP_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a skill group with a given id
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": RECIPE_GROUP_EXAMPLE}}  # type: ignore # noqa E501


class RecipeViewSet(BoundlexxViewSet):
    queryset = (
        Recipe.objects.all()
        .select_related("output")
        .prefetch_related(
            "requirements",
            "tints",
            "levels",
            "levels__inputs",
            "levels__inputs__group",
            "levels__inputs__item",
            "requirements__skill",
        )
    )
    serializer_class = RecipeSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilterSet

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of recipes avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(RECIPE_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a recipe with a given id
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": RECIPE_EXAMPLE}}  # type: ignore # noqa E501
