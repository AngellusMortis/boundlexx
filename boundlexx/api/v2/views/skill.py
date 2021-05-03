from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import (
    DedupedFilter,
    LocalizationFilterSet,
    SkillFilterSet,
)
from boundlexx.api.common.serializers import SkillGroupSerializer, SkillSerializer
from boundlexx.api.common.viewsets import BoundlexxReadOnlyViewSet
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.boundless.models import Skill, SkillGroup


class SkillGroupViewSet(BoundlexxReadOnlyViewSet):
    schema = DescriptiveAutoSchema(tags=["skills"])
    queryset = (
        SkillGroup.objects.all()
        .select_related("display_name")
        .prefetch_related("display_name__strings")
    )
    serializer_class = SkillGroupSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = LocalizationFilterSet
    ordering = ["-rank", "id"]
    ordering_fields: list[str] = []
    search_fields = [
        "name",
        "display_name__strings__text",
    ]

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of skill groups avaiable in Boundless
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

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


class SkillViewSet(BoundlexxReadOnlyViewSet):
    queryset = (
        Skill.objects.all()
        .select_related("group", "description", "display_name")
        .prefetch_related("description__strings", "display_name__strings")
    )
    serializer_class = SkillSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = SkillFilterSet
    ordering = ["-rank", "id"]
    ordering_fields: list[str] = []
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
