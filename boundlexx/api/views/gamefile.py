from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from boundlexx.api.serializers import GameFileSerializer, SimpleGameFileSerializer
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.views.mixins import DescriptiveAutoSchemaMixin
from boundlexx.ingest.models import GameFile

GAMEFILE_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/game-files/1/",
    "folder": "",
    "filename": "config.json",
    "file_type": "JSON",
    "game_version": "246.6.0",
    "content": {"steamEnabled": True},
}

GAMEFILE_LIST_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/game-files/1/",
    "folder": "",
    "filename": "config.json",
    "file_type": "JSON",
    "game_version": "246.6.0",
}


class GameFileViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = GameFile.objects.all()
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

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.detail_serializer_class

        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of game files from the game Boundless.

        Requires authentication. Provide `Authorization: Token <token>` header.
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(GAMEFILE_LIST_EXAMPLE)}}  # type: ignore # noqa E501

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

    retrieve.example = {"retrieve": {"value": GAMEFILE_EXAMPLE}}  # type: ignore # noqa E501
