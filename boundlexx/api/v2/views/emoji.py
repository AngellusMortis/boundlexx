from django.db.models import Q
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_fuzzysearch.search import RankedFuzzySearchFilter

from boundlexx.api.common.filters import DedupedFilter, EmojiFilterSet
from boundlexx.api.common.serializers import EmojiSerializer
from boundlexx.api.common.viewsets import BoundlexxReadOnlyViewSet
from boundlexx.boundless.models import Emoji


class EmojiViewSet(BoundlexxReadOnlyViewSet):
    queryset = Emoji.objects.filter(active=True).prefetch_related("emojialtname_set")
    serializer_class = EmojiSerializer
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
        obj = queryset.filter(
            Q(name=lookup_name) | Q(emojialtname__name=lookup_name)
        ).first()

        if obj is None:
            raise Http404()

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
