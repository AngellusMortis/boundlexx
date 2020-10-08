from rest_framework import viewsets

from boundlexx.api.common.mixins import DescriptiveAutoSchemaMixin
from boundlexx.api.common.serializers import BlockSerializer
from boundlexx.boundless.models import Block


class BlockViewSet(
    DescriptiveAutoSchemaMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = Block.objects.filter(block_item__isnull=False).order_by("game_id")
    serializer_class = BlockSerializer
    lookup_field = "game_id"

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of blocks with their item mapping
        """

        return super().list(request, *args, **kwargs)  # pylint: disable=no-member

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):  # pylint: disable=arguments-differ
        """
        Retrieves a block with its item mapping
        """
        return super().retrieve(request, *args, **kwargs)  # pylint: disable=no-member
