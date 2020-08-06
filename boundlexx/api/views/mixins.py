from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend

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
