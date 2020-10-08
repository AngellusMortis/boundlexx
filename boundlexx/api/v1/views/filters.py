from django.db.models import F, Func, Q, Value
from django.utils.translation import ugettext as _
from django_filters.rest_framework import filters

from boundlexx.api.common.filters import BaseFilterSet, LocalizationFilterSet
from boundlexx.boundless.models import Recipe, ResourceCount, WorldBlockColor


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
