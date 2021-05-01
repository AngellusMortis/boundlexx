from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.db.models import F, Func, Q, Value
from django.utils.translation import gettext as _
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import BaseFilterBackend

from boundlexx.boundless.models import (
    Emoji,
    Item,
    Recipe,
    ResourceCount,
    World,
    WorldBlockColor,
)
from boundlexx.boundless.utils import (
    get_block_color_item_ids,
    get_block_metal_item_ids,
    get_world_block_color_item_ids,
)

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


class EmojiFilterSet(BaseFilterSet):
    class Meta:
        model = Emoji
        fields = ["category"]


class ItemFilterSet(LocalizationFilterSet):
    has_colors = filters.BooleanFilter(
        label=_("Filters out items with/without colors"),
        method="filter_colors",
    )

    has_metal_variants = filters.BooleanFilter(
        label=_("Filters out items with/without metal variants"),
        method="filter_metals",
    )

    has_world_colors = filters.BooleanFilter(
        label=_(
            "Filters out items that vary from world to world with "
            "colors (rock, grass, wood, etc.)"
        ),
        method="filter_world_colors",
    )

    class Meta:
        model = Item
        fields = [
            "string_id",
            "item_subtitle_id",
            "list_type__string_id",
            "is_resource",
        ]

    def filter_colors(self, queryset, name, value):
        if value:
            queryset = queryset.filter(game_id__in=get_block_color_item_ids())
        elif value is False:
            queryset = queryset.exclude(game_id__in=get_block_color_item_ids())

        return queryset

    def filter_metals(self, queryset, name, value):
        if value:
            queryset = queryset.filter(game_id__in=get_block_metal_item_ids())
        elif value is False:
            queryset = queryset.exclude(game_id__in=get_block_metal_item_ids())

        return queryset

    def filter_world_colors(self, queryset, name, value):
        if value:
            queryset = queryset.filter(game_id__in=get_world_block_color_item_ids())
        elif value is False:
            queryset = queryset.exclude(game_id__in=get_world_block_color_item_ids())

        return queryset


class RecipeFilterSet(LocalizationFilterSet):
    input_id = filters.NumberFilter(method="filter_input")
    output_id = filters.NumberFilter(method="filter_output")
    is_event = filters.BooleanFilter(method="filter_event")
    requires_backer = filters.BooleanFilter(method="filter_backer")

    class Meta:
        model = Recipe
        fields = [
            "machine",
        ]

    def filter_input(self, queryset, name, value):
        return queryset.filter(
            Q(levels__inputs__item__game_id=value)
            | Q(levels__inputs__group__members__game_id=value)
        )

    def filter_output(self, queryset, name, value):
        return queryset.filter(output__game_id=value)

    def filter_event(self, queryset, name, value):
        if value:
            queryset = queryset.filter(required_event__isnull=False)
        elif value is False:
            queryset = queryset.filter(required_event__isnull=True)
        return queryset

    def filter_backer(self, queryset, name, value):
        if value:
            queryset = queryset.filter(required_backer_tier__isnull=False)
        elif value is False:
            queryset = queryset.filter(required_backer_tier__isnull=True)
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
    is_default = filters.BooleanFilter(
        label=_("Show colors world spawned with"),
        method="filter_null",
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
            "Filters end based on a given time contraint. `end_after` sets "
            "lower bound and `end_before` sets upper bound. Format is "
            "<a href='https://en.wikipedia.org/wiki/ISO_8601'>ISO 8601</a>"
        ),
    )
    last_updated = filters.IsoDateTimeFromToRangeFilter(
        label=_(
            "Filters last_updated based on a given time contraint. "
            "`last_updated_after` sets lower bound and `last_updated_before` sets "
            "upper bound. Format is <a href='https://en.wikipedia.org/wiki/ISO_8601'>"
            "ISO 8601</a>"
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


class WorldBlockColorFilterSet(BaseFilterSet):
    is_exo = filters.BooleanFilter(
        label=_("Filter out exo/non exoworlds"), method="filter_exo"
    )
    is_sovereign = filters.BooleanFilter(
        label=_("Filter out Sovereign/non Sovereign worlds"),
        method="filter_sovereign",
    )
    show_inactive_colors = filters.BooleanFilter(
        label=_("Include previous avaiable Sovereign colors"),
        method="filter_null",
    )
    show_inactive = filters.BooleanFilter(
        label=_("Include inactive worlds (no longer in game API)"),
        method="filter_null",
    )

    class Meta:
        model = WorldBlockColor
        fields = [
            "active",
            "is_default",
            "item__string_id",
            "item__game_id",
            "world__active",
            "world__tier",
            "world__region",
            "world__world_type",
            "world__name",
            "world__display_name",
        ]

    def filter_exo(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                world__assignment__isnull=False,
                world__owner__isnull=True,
                world__end__isnull=False,
            )
        elif value is False:
            queryset = queryset.exclude(
                world__assignment__isnull=False,
                world__owner__isnull=True,
                world__end__isnull=False,
            )

        return queryset

    def filter_sovereign(self, queryset, name, value):
        if value:
            queryset = queryset.filter(world__owner__isnull=False)
        elif value is False:
            queryset = queryset.filter(world__owner__isnull=True)
        return queryset

    def filter_null(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if (
            self.form.cleaned_data["show_inactive_colors"] is not True
            and self.form.cleaned_data["active"] is None
        ):
            queryset = queryset.filter(active=True)

        if (
            self.form.cleaned_data["show_inactive"] is not True
            and self.form.cleaned_data["world__active"] is None
        ):
            queryset = queryset.filter(world__active=True)

        return queryset


class ItemColorFilterSet(WorldBlockColorFilterSet):
    show_inactive_colors = filters.BooleanFilter(
        label=_("Include previous avaiable Sovereign colors"),
        method="filter_null",
    )
    show_inactive = filters.BooleanFilter(
        label=_("Include inactive worlds (no longer in game API)"),
        method="filter_null",
    )

    class Meta:
        model = WorldBlockColor
        fields = [
            "active",
            "is_default",
            "color__game_id",
            "world__active",
            "world__tier",
            "world__region",
            "world__world_type",
            "world__name",
            "world__display_name",
        ]

    def filter_null(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if (
            self.form.cleaned_data["show_inactive_colors"] is not True
            and self.form.cleaned_data["active"] is None
        ):
            queryset = queryset.filter(active=True)

        if (
            self.form.cleaned_data["show_inactive"] is not True
            and self.form.cleaned_data["world__active"] is None
        ):
            queryset = queryset.filter(world__active=True)

        return queryset


class ItemResourceCountFilterSet(BaseFilterSet):
    is_exo = filters.BooleanFilter(
        label=_("Filter out exo/non exoworlds"), method="filter_exo"
    )
    is_sovereign = filters.BooleanFilter(
        label=_("Filter out Sovereign/non Sovereign worlds"),
        method="filter_sovereign",
    )

    class Meta:
        model = ResourceCount
        fields = [
            "world_poll__world__tier",
            "world_poll__world__region",
            "world_poll__world__world_type",
            "world_poll__world__name",
            "world_poll__world__display_name",
        ]

    def filter_exo(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                world_poll__world__assignment__isnull=False,
                world_poll__world__owner__isnull=True,
                world_poll__world__end__isnull=False,
            )
        elif value is False:
            queryset = queryset.exclude(
                world_poll__world__assignment__isnull=False,
                world_poll__world__owner__isnull=True,
                world_poll__world__end__isnull=False,
            )

        return queryset

    def filter_sovereign(self, queryset, name, value):
        if value:
            queryset = queryset.filter(world_poll__world__owner__isnull=False)
        elif value is False:
            queryset = queryset.filter(world_poll__world__owner__isnull=True)
        return queryset


class TimeseriesFilterSet(BaseFilterSet):
    time = filters.IsoDateTimeFromToRangeFilter(
        method="filter_time",
        label=_(
            "Filters based on a given time contraint. `time_after` sets "
            "lower bound and `time_before` sets upper bound. Format is "
            "<a href='https://en.wikipedia.org/wiki/ISO_8601'>ISO 8601</a>"
        ),
    )
    bucket = filters.CharFilter(
        method="filter_bucket",
        label=(
            "Bucket size. Example `1 day`, `4 hours`. Bucket filter only "
            "applies to `/stats` endpoint"
        ),
    )

    def filter_time(self, queryset, name, value):
        if value.start is not None:
            queryset = queryset.filter(time__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(time__lte=value.stop)

        return queryset

    def filter_bucket(self, queryset, name, value):
        return queryset.annotate(
            time_bucket=Func(Value(value), F("time"), function="time_bucket")
        )
