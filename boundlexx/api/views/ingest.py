import json

from rest_framework import views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boundlexx.boundless.models import (
    Color,
    Item,
    World,
    WorldBlockColor,
    WorldCreatureColor,
)


class WorldWSDataView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_data(self, request):
        display_name = None
        block_colors = []
        creature_colors = []

        try:
            display_name = request.data["config"]["displayName"]
            for key, value in request.data["config"]["world"][
                "blockColors"
            ].items():
                block_colors.append((key, value))

            for key, value in request.data["config"]["world"][
                "creatureColors"
            ].items():
                creature_colors.append((key, value))
        except Exception:  # pylint: disable=broad-except
            return None

        return (display_name, block_colors, creature_colors)

    def post(self, request, *args, **kwargs):
        data = self._get_data(request)

        if data is None:
            return Response(status=400)

        world = World.objects.filter(display_name=data[0]).first()

        if world is None:
            world = World.objects.get_or_create_unknown_world(
                {"name": data[0]}
            )

        block_colors_created = 0
        creature_colors_created = 0
        block_colors_created = 0
        for block_color in data[1]:
            item = Item.objects.filter(
                string_id=f"ITEM_TYPE_{block_color[0]}"
            ).first()

            if item is not None:
                color = Color.objects.get(game_id=block_color[1])

                _, created = WorldBlockColor.objects.get_or_create(
                    world=world, item=item, defaults={"color": color}
                )

                if created:
                    block_colors_created += 1

        for creature_color in data[2]:
            _, created = WorldCreatureColor.objects.get_or_create(
                world=world,
                creature_type=creature_color[0],
                defaults={"color_data": json.dumps(creature_color[1])},
            )

            if created:
                creature_colors_created += 1

        return Response(
            status=200,
            data={
                "blocks": block_colors_created,
                "creatures": creature_colors_created,
            },
        )
