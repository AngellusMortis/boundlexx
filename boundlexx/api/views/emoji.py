from typing import List

from rest_framework import viewsets

from boundlexx.api.serializers import EmojiSerializer
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.views.mixins import DescriptiveAutoSchemaMixin
from boundlexx.boundless.models import Emoji

EMOJI_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/emojis/black_joker/",
    "name": "black_joker",
    "image_url": "https://cdn.boundlexx.app/local-worlds/emoji/black_joker_7WaYJvl.png",
}


class EmojiViewSet(DescriptiveAutoSchemaMixin, viewsets.ReadOnlyModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = Emoji.objects.all()
    serializer_class = EmojiSerializer
    lookup_field = "name"
    ordering_fields: List[str] = []

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of emojis from the game Boundless.
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    list.example = {"list": {"value": get_list_example(EMOJI_EXAMPLE)}}  # type: ignore # noqa E501

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves an emojis from the game Boundless.
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member

    retrieve.example = {"retrieve": {"value": EMOJI_EXAMPLE}}  # type: ignore # noqa E501
