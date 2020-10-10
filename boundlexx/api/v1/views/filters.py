from django.db.models import F, Func, Value
from django.utils.translation import ugettext as _
from django_filters.rest_framework import filters

from boundlexx.api.common.filters import BaseFilterSet


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
