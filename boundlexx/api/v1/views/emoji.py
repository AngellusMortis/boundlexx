from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter, EmojiFilterSet
from boundlexx.api.common.viewsets import BoundlexxReadOnlyViewSet
from boundlexx.api.utils import get_base_url, get_list_example
from boundlexx.api.v1.serializers import URLEmojiSerializer
from boundlexx.boundless.models import Emoji

EMOJI_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/emojis/black_joker/",
    "name": "black_joker",
    "image_url": "https://cdn.boundlexx.app/local-worlds/emoji/black_joker_7WaYJvl.png",
}


class EmojiViewSet(BoundlexxReadOnlyViewSet):
    queryset = Emoji.objects.filter(active=True).prefetch_related("emojialtname_set")
    serializer_class = URLEmojiSerializer
    lookup_field = "name"
    filter_backends = [
        DjangoFilterBackend,
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    filterset_class = EmojiFilterSet
    search_fields = ["name", "emojialtname__name"]
    ordering = ["-rank", "name"]
    ordering_fields: list[str] = []

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_name = self.kwargs[self.lookup_field]
        obj = get_object_or_404(
            queryset, Q(name=lookup_name) | Q(emojialtname__name=lookup_name)
        )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

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
