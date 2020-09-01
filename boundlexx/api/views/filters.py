from django.conf import settings
from django.db.models import F, Func, Value
from django.utils.translation import ugettext as _
from django_filters.rest_framework import FilterSet, filters

from boundlexx.boundless.models import (
    Item,
    ResourceCount,
    World,
    WorldBlockColor,
)
from boundlexx.boundless.utils import get_block_color_item_ids


class LangFilter(filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs["label"] = _("Filters the list of localized named returned.")
        kwargs["choices"] = settings.BOUNDLESS_LANGUAGES

        super().__init__(*args, **kwargs)

    def filter(self, qs, value):  # noqa: A003
        return qs


class LocalizationFilterSet(FilterSet):
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


class WorldFilterSet(FilterSet):
    is_exo = filters.BooleanFilter(
        label=_("Filter out exo/non exoworlds"), method="filter_exo"
    )
    is_sovereign = filters.BooleanFilter(
        label=_("Filter out Sovereign/non Sovereign worlds"),
        method="filter_sovereign",
    )
    show_inactive = filters.BooleanFilter(
        label=_("Include inactive worlds (no longer in game API)"),
        method="filter_inactive",
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

    def filter_inactive(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if "id" not in self.request.parser_context["kwargs"]:
            if self.form.cleaned_data["show_inactive"] is not True:
                queryset = queryset.filter(active=True)

        return queryset


class WorldBlockColorFilterSet(FilterSet):
    is_exo = filters.BooleanFilter(
        label=_("Filter out exo/non exoworlds"), method="filter_exo"
    )
    is_sovereign = filters.BooleanFilter(
        label=_("Filter out Sovereign/non Sovereign worlds"),
        method="filter_sovereign",
    )

    class Meta:
        model = WorldBlockColor
        fields = [
            "item__string_id",
            "item__game_id",
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


class ItemResourceCountFilterSet(FilterSet):
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
    class Meta:
        model = WorldBlockColor
        fields = [
            "color__game_id",
            "world__tier",
            "world__region",
            "world__world_type",
            "world__name",
            "world__display_name",
        ]


class TimeseriesFilterSet(FilterSet):
    time = filters.DateTimeFromToRangeFilter(
        method="filter_time",
        label=_(
            "Filters based on a given time contraint. `time_after` sets "
            "lower bound and `time_before` sets upper bound. Format is "
            "`YYYY-MM-DD HH:MM` or `YYYY-MM-DD`. Time is specified in "
            "local timezone;  automatically handles and converts to proper "
            "time."
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
