from django.conf import settings
from django.utils.translation import ugettext as _
from django_filters.rest_framework import FilterSet, filters

from boundlexx.boundless.models import World


class LocalizationFilterSet(FilterSet):
    lang = filters.ChoiceFilter(
        label=_("Filters the list of localized named returned."),
        choices=settings.BOUNDLESS_LANGUAGES,
    )

    def filter_queryset(self, queryset):
        return queryset


class WorldFilterSet(FilterSet):
    is_exo = filters.BooleanFilter(
        label="Filter out exo/non exoworlds", method="filter_exo"
    )
    is_sovereign = filters.BooleanFilter(
        label="Filter out Sovereign/non Sovereign worlds",
        method="filter_sovereign",
    )

    class Meta:
        model = World
        fields = [
            "tier",
            "region",
            "world_type",
            "assignment",
            "is_creative",
            "is_locked",
            "is_public",
        ]

    def filter_exo(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                assignment__isnull=False, owner__isnull=True, end__isnull=False
            )
        elif value is False:
            queryset = queryset.exclude(
                assignment__isnull=False, owner__isnull=True, end__isnull=False
            )

        return queryset

    def filter_sovereign(self, queryset, name, value):
        if value:
            queryset = queryset.filter(owner__isnull=False)
        elif value is False:
            queryset = queryset.filter(owner__isnull=True)
        return queryset
