from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from boundlexx.api.common.mixins import DescriptiveAutoSchemaMixin


class BoundlexxViewSet(DescriptiveAutoSchemaMixin, ReadOnlyModelViewSet):
    def get_serializer_class(self):
        if self.action == "retrieve" and hasattr(self, "detail_serializer_class"):
            return (  # pylint: disable=no-member  # type: ignore
                self.detail_serializer_class
            )

        return super().get_serializer_class()

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
