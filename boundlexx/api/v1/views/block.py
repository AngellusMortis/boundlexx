from boundlexx.api.common.viewsets import BoundlexxViewSet
from boundlexx.api.v1.serializers import URLBlockSerializer
from boundlexx.boundless.models import Block


class BlockViewSet(
    BoundlexxViewSet,
):
    queryset = (
        Block.objects.filter(block_item__isnull=False)
        .select_related("block_item")
        .order_by("game_id")
    )
    serializer_class = URLBlockSerializer
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
