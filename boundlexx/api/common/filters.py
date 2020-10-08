from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.utils.translation import ugettext as _
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import BaseFilterBackend

from boundlexx.boundless.models import Item, World
from boundlexx.boundless.utils import get_block_color_item_ids

DEFAULT_FILTERS = ["limit", "offset", "ordering", "search", "format"]


class DedupedFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # only remove duplicates from list views with search results
        if view.detail or "search" not in request.query_params:
            return queryset

        pks = set()
        final_result = []
        for item in list(queryset):
            if item.pk not in pks:
                final_result.append(item)
                pks.add(item.pk)

        return final_result


class BaseFilterSet(FilterSet):
    def filter_queryset(self, queryset):
        allowed_filters = set(DEFAULT_FILTERS)

        for key, field in self.form.fields.items():
            if isinstance(field, filters.IsoDateTimeFromToRangeFilter.field_class):
                allowed_filters.add(f"{key}_before")
                allowed_filters.add(f"{key}_after")
            else:
                allowed_filters.add(key)

        actual_filters = set(self.request.query_params.keys())

        disallowed = actual_filters - allowed_filters
        if len(disallowed) > 0:
            raise SuspiciousOperation("Invalid Filter")

        return super().filter_queryset(queryset)


class LangFilter(filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs["label"] = _("Filters the list of localized named returned.")
        kwargs["choices"] = settings.BOUNDLESS_LANGUAGES + [
            ("none", "None"),
            ("all", "All"),
        ]

        super().__init__(*args, **kwargs)

    def filter(self, qs, value):  # noqa: A003
        return qs


class LocalizationFilterSet(BaseFilterSet):
    lang = LangFilter()


class ItemFilterSet(LocalizationFilterSet):
    has_colors = filters.BooleanFilter(
        label=_("Filters out items with/without colors"),
        method="filter_colors",
    )

    is_resource = filters.BooleanFilter(
        label=_("Filters out items that are/are not resources"),
        method="filter_resources",
    )

    class Meta:
        model = Item
        fields = [
            "string_id",
        ]

    def filter_resources(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                game_id__in=settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING
            )
        elif value is False:
            queryset = queryset.exclude(
                game_id__in=settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING
            )

        return queryset

    def filter_colors(self, queryset, name, value):
        if value:
            queryset = queryset.filter(game_id__in=get_block_color_item_ids())
        elif value is False:
            queryset = queryset.exclude(game_id__in=get_block_color_item_ids())

        return queryset


class SkillFilterSet(LocalizationFilterSet):
    group = filters.CharFilter(method="filter_group")

    def filter_group(self, queryset, name, value):
        return queryset.filter(group__name=value)


class WorldFilterSet(BaseFilterSet):
    is_exo = filters.BooleanFilter(
        label=_("Filter out exo/non exoworlds"), method="filter_exo"
    )
    is_sovereign = filters.BooleanFilter(
        label=_("Filter out Sovereign/non Sovereign worlds"),
        method="filter_sovereign",
    )
    show_inactive = filters.BooleanFilter(
        label=_("Include inactive worlds (no longer in game API)"),
        method="filter_null",
    )
    show_inactive_colors = filters.BooleanFilter(
        label=_("Include previous colors for world (Sovereign only)"),
        method="filter_null",
    )
    start = filters.IsoDateTimeFromToRangeFilter(
        label=_(
            "Filters start based on a given time contraint. `start_after` sets "
            "lower bound and `start_before` sets upper bound. Format is "
            "<a href='https://en.wikipedia.org/wiki/ISO_8601'>ISO 8601</a>"
        ),
    )
    end = filters.IsoDateTimeFromToRangeFilter(
        label=_(
            "Filters start based on a given time contraint. `end_after` sets "
            "lower bound and `end_before` sets upper bound. Format is "
            "<a href='https://en.wikipedia.org/wiki/ISO_8601'>ISO 8601</a>"
        ),
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
            "special_type",
            "start",
            "end",
            "active",
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

    def filter_null(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if (
            "id" not in self.request.parser_context["kwargs"]
            and self.form.cleaned_data["active"] is None
        ):
            if self.form.cleaned_data["show_inactive"] is not True:
                queryset = queryset.filter(active=True)

        return queryset
