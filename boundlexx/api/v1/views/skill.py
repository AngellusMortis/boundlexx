from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import (
    DedupedFilter,
    LocalizationFilterSet,
    SkillFilterSet,
)
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.v1.serializers import URLSkillGroupSerializer, URLSkillSerializer
from boundlexx.boundless.models import Skill, SkillGroup

SKILL_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/skills/77/",
    "name": "Slingbow Epic",
    "display_name": {
        "string_id": "GUI_SKILLS_SLINGBOW_EPIC_TITLE",
        "strings": [
            {
                "lang": "french",
                "text": "lance-flèche épique",
                "plain_text": "lance-flèche épique",
            },
            {
                "lang": "german",
                "text": "Epischer Schleuderbogen",
                "plain_text": "Epischer Schleuderbogen",
            },
            {"lang": "english", "text": "Slingbow Epic", "plain_text": "Slingbow Epic"},
            {
                "lang": "italian",
                "text": "Arcofionda epica",
                "plain_text": "Arcofionda epica",
            },
            {"lang": "spanish", "text": "Honda épica", "plain_text": "Honda épica"},
        ],
    },
}

SKILL_GROUP_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/skill-groups/1/",
    "name": "Epic 1",
    "skill_type": "Epic",
    "display_name": {
        "string_id": "GUI_SKILLS_GROUP_EPIC_1",
        "strings": [
            {"lang": "french", "text": "Épique 1", "plain_text": "Épique 1"},
            {"lang": "german", "text": "Episch 1", "plain_text": "Episch 1"},
            {"lang": "english", "text": "Epic 1", "plain_text": "Epic 1"},
            {"lang": "italian", "text": "Epico 1", "plain_text": "Epico 1"},
            {"lang": "spanish", "text": "Épico 1", "plain_text": "Épico 1"},
        ],
    },
    "unlock_level": 6,
}


class SkillGroupViewSet(BoundlexxViewSet):
    schema = DescriptiveAutoSchema(tags=["Skills"])

    queryset = (
        SkillGroup.objects.all()
        .select_related("display_name")
        .prefetch_related("display_name__strings")
    )
    serializer_class = URLSkillGroupSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = LocalizationFilterSet
    ordering = ["-rank", "id"]
    ordering_fields: List[str] = []
    search_fields = [
        "name",
        "display_name__strings__text",
    ]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of skill groups avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(SKILL_GROUP_EXAMPLE)}}  # type: ignore # noqa E501

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

    retrieve.example = {"retrieve": {"value": SKILL_GROUP_EXAMPLE}}  # type: ignore # noqa E501


class SkillViewSet(BoundlexxViewSet):
    queryset = (
        Skill.objects.all()
        .select_related("group", "description", "display_name")
        .prefetch_related("description__strings", "display_name__strings")
    )
    serializer_class = URLSkillSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = SkillFilterSet
    ordering = ["-rank", "id"]
    ordering_fields: List[str] = []
    search_fields = [
        "name",
        "description__strings__text",
        "display_name__strings__text",
    ]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of skills avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(SKILL_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a skill with a given id
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": SKILL_EXAMPLE}}  # type: ignore # noqa E501
