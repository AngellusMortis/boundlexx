from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from bge.api.serializers import ColorSerializer
from bge.boundless.models import Color


class ColorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Color.objects.all().order_by("game_id")
    serializer_class = ColorSerializer

    def list(self, request, *args, **kwargs):  # noqa A003
        """
        Retrieves the list of colors avaiable in Boundless
        """

        return super().list(  # pylint: disable=no-member
            request, *args, **kwargs
        )

    def retrieve(self, request, pk=None):  # pylint: disable=arguments-differ
        """
        Retrieves a color with a given ID
        """
        color = get_object_or_404(self.get_queryset(), game_id=pk)
        serializer = self.get_serializer_class()(color)
        return Response(serializer.data)
