from typing import TYPE_CHECKING

from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from boundlexx.api.common.mixins import DescriptiveAutoSchemaMixin

if TYPE_CHECKING:
    from rest_framework.viewsets import ModelViewSet as _Base
else:
    _Base = object


class BoundlexxViewSetMixin(DescriptiveAutoSchemaMixin, _Base):
    action: str

    def get_serializer_class(self):
        if self.action == "retrieve" and hasattr(self, "detail_serializer_class"):
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_response_serializer_class(self):
        if hasattr(self, "response_serializer_class"):
            return self.response_serializer_class
        return self.get_serializer_class()

    def get_response_serializer(self, *args, **kwargs):
        serializer_class = self.get_response_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class BoundlexxListViewSetMixin(BoundlexxViewSetMixin, _Base):
    def list(self, request, *args, **kwargs):  # noqa A003
        queryset = self.filter_queryset(self.get_queryset())

        if not isinstance(queryset, list):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        elif self.paginator is not None:
            self.paginator.offset = 0
            self.paginator.limit = self.paginator.get_limit(request)
            if len(queryset) > self.paginator.limit:
                queryset = queryset[: self.paginator.limit]

            self.paginator.count = len(queryset)
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BoundlexxGenericViewSet(BoundlexxListViewSetMixin, GenericViewSet):
    pass


class BoundlexxListViewSet(BoundlexxListViewSetMixin, ListModelMixin, GenericViewSet):
    pass


class BoundlexxReadOnlyViewSet(BoundlexxListViewSetMixin, ReadOnlyModelViewSet):
    pass
