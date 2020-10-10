from django_filters.rest_framework import DjangoFilterBackend

from boundlexx.api.common.filters import LocalizationFilterSet, RecipeFilterSet
from boundlexx.api.common.serializers import RecipeGroupSerializer, RecipeSerializer
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.boundless.models import Recipe, RecipeGroup


class RecipeGroupViewSet(BoundlexxViewSet):
    schema = DescriptiveAutoSchema(tags=["Recipes"])

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
