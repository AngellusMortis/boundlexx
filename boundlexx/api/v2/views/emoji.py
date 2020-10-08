from typing import List

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter
from boundlexx.api.common.serializers import EmojiSerializer
from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.boundless.models import Emoji


class EmojiViewSet(BoundlexxViewSet):
    queryset = Emoji.objects.filter(active=True).prefetch_related("emojialtname_set")
    serializer_class = EmojiSerializer
    lookup_field = "name"
    filter_backends = [
        RankedFuzzySearchFilter,
        filters.OrderingFilter,
        DedupedFilter,
    ]
    search_fields = ["name", "emojialtname__name"]
    ordering = ["-rank", "name"]
    ordering_fields: List[str] = []

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
