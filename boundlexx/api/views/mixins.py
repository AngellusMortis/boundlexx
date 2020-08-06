from typing import Dict, List, Optional

from django.db.models import Avg, Func, Max, Min, StdDev, Variance
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.api.views.filters import TimeseriesFilterSet
from boundlexx.api.views.pagination import TimeseriesPagination


class DescriptiveAutoSchemaMixin:
    schema = DescriptiveAutoSchema()


class TimeseriesMixin:
    is_timeseries = True
    pagination_class = TimeseriesPagination
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = TimeseriesFilterSet
    time_bucket_serializer_class: Optional[BaseSerializer] = None
    number_fields: List[str] = []

    def get_queryset(self):
        return super().get_queryset().order_by("-time")  # type: ignore

    def get_parents_query_dict(self):
        kwargs = super().get_parents_query_dict()  # type: ignore

        value = kwargs.get(self.lookup_field)  # type: ignore
        if value == "latest":
            kwargs.pop(self.lookup_field)  # type: ignore

        return kwargs

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())  # type: ignore

        if self.kwargs[self.lookup_field] == "latest":  # type: ignore
            queryset = queryset[:1]

            if queryset.count() == 1:
                obj = queryset.first()
                self.check_object_permissions(self.request, obj)  # type: ignore # noqa E501
                return obj
            raise Http404()

        return super().get_object()  # type: ignore

    def stats(self, request, **kwargs):
        if self.time_bucket_serializer_class is None:
            raise Http404()

        queryset = self.filter_queryset(self.get_queryset())  # type: ignore

        is_bucket = "bucket" in request.query_params
        values_list = ["time_bucket"]

        if len(self.number_fields) > 0:
            aggregate_args: Dict[str, Func] = {}
            for field in self.number_fields:
                avg_field = field + "_average"
                min_field = field + "_min"
                max_field = field + "_max"
                stddev_field = field + "_stddev"
                variance_field = field + "_variance"

                aggregate_args[avg_field] = Avg(field)
                aggregate_args[min_field] = Min(field)
                aggregate_args[max_field] = Max(field)
                aggregate_args[stddev_field] = StdDev(field)
                aggregate_args[variance_field] = Variance(field)

                values_list.append(avg_field)
                values_list.append(min_field)
                values_list.append(max_field)
                values_list.append(stddev_field)
                values_list.append(variance_field)

            if is_bucket:
                queryset = queryset.annotate(**aggregate_args)
            else:
                queryset = [queryset.aggregate(**aggregate_args)]

        if is_bucket:
            queryset = queryset.values(*values_list).order_by("time_bucket")

        serializer = self.time_bucket_serializer_class(  # pylint: disable=not-callable  # noqa: E501
            queryset, many=True
        )

        return Response(serializer.data)

    @classmethod
    def get_extra_actions(cls):
        extra_actions = super().get_extra_actions()  # type: ignore

        if cls.time_bucket_serializer_class is not None:
            extra_actions.append(
                action(
                    detail=False,
                    methods=["get"],
                    serializer_class=cls.time_bucket_serializer_class,
                )(cls.stats)
            )

        return extra_actions
