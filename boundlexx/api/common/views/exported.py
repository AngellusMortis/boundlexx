from django_filters.rest_framework import DjangoFilterBackend

from boundlexx.api.common.serializers import ExportedFileSerializer
from boundlexx.api.common.viewsets import BoundlexxListViewSet
from boundlexx.api.models import ExportedFile


class ExportedFileViewSet(BoundlexxListViewSet):
    queryset = ExportedFile.objects.all().order_by("name")
    serializer_class = ExportedFileSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
    ]
    ordering = ["-rank", "id"]
    ordering_fields: list[str] = []

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of game files from the game Boundless.

        Requires authentication. Provide `Authorization: Token <token>` header.
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.operation_id = "listExportedFiles"  # type: ignore # noqa E501
