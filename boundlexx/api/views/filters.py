from django.conf import settings
from django.utils.translation import ugettext as _
from django_filters.rest_framework import FilterSet, filters


class LocalizationFilterSet(FilterSet):
    lang = filters.ChoiceFilter(
        label=_("Filters the list of localized named returned."),
        choices=settings.BOUNDLESS_LANGUAGES,
    )

    def filter_queryset(self, queryset):
        return queryset
