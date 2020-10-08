from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from boundlexx.api.common.serializers import (
    GameFileSerializer,
    SimpleGameFileSerializer,
)
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.ingest.models import GameFile


class GameFileViewSet(BoundlexxViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = (
        GameFile.objects.all()
        .order_by("folder", "filename", "-game_version")
        .distinct("folder", "filename")
    )
    serializer_class = SimpleGameFileSerializer
    detail_serializer_class = GameFileSerializer
    lookup_field = "id"
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_fields = [
        "folder",
        "filename",
        "file_type",
    ]
    ordering = ["-rank", "id"]
    ordering_fields: List[str] = []

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of game files from the game Boundless.

        Requires authentication. Provide `Authorization: Token <token>` header.
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.operation_id = "listGameFiles"  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a decoded game file from the game Boundless.

        Requires authentication. Provide `Authorization: Token <token>` header.
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.operation_id = "retrieveGameFile"  # type: ignore # noqa E501
