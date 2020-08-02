import json
import logging
import traceback

from rest_framework import views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boundlexx.boundless.client import BoundlessClient
from boundlexx.boundless.models import (
    Color,
    Item,
    World,
    WorldBlockColor,
    WorldCreatureColor,
)
from boundlexx.boundless.tasks import poll_worlds

logger = logging.getLogger("ingest")


class WorldWSDataView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_data(self, request):
        world_id = None
        display_name = None
        block_colors = []
        creature_colors = []

        try:
            if "world_id" in request.data:
                world_id = int(request.data["world_id"])
            elif "display_name" in request.data:
                display_name = request.data["display_name"]
            else:
                display_name = request.data.get("config", {}).get(
                    "displayName"
                )

            for key, value in request.data["config"]["world"][
                "blockColors"
            ].items():
                block_colors.append((key, value))

            for key, value in request.data["config"]["world"][
                "creatureColors"
            ].items():
                creature_colors.append((key, value))
        except Exception:  # pylint: disable=broad-except
            logger.warning(traceback.format_exc())
            return None

        if world_id is None and display_name is None:
            return None

        return (world_id, display_name, block_colors, creature_colors)

    def _get_world(self, world_id, display_name):
        if world_id is not None:
            world = World.objects.filter(id=world_id).first()
            if world is None:
                c = BoundlessClient()
                world_data = c.get_world_data(world_id)
                world, _ = World.objects.get_or_create_from_game_dict(
                    world_data["worldData"]
                )
        else:
            world = World.objects.filter(display_name=display_name).first()

            if world is None:
                world, created = World.objects.get_or_create_unknown_world(
                    {"name": display_name}
                )

                if created:
                    poll_worlds.delay([world])

        return world

    def post(self, request, *args, **kwargs):
        data = self._get_data(request)

        if data is None:
            logger.warning("Bad ingest data:\n%s", request.data)
            return Response(status=400)

        world = self._get_world(data[0], data[1])

        block_colors_created = 0
        creature_colors_created = 0
        block_colors_created = 0
        for block_color in data[2]:
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

        for creature_color in data[3]:
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
