import json
import logging
import traceback

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from boundlexx.api.common.serializers import (
    WebsocketResponseSerializer,
    WebsocketSerializer,
    WorldControlSerializer,
    WorldControlSimpleSerializer,
    WorldForumIDSerializer,
)
from boundlexx.api.common.viewsets import BoundlexxGenericViewSet
from boundlexx.api.permissions import IsWorldTrusted
from boundlexx.boundless.game import BoundlessClient
from boundlexx.boundless.models import World, WorldBlockColor, WorldCreatureColor
from boundlexx.boundless.tasks import add_world_control_data, recalculate_and_send_exo

logger = logging.getLogger("ingest")


class WorldWSDataView(BoundlexxGenericViewSet):
    """
    Accepts World config object from the Boundless game Websocket.

    Requires API Key.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = WebsocketSerializer
    response_serializer_class = WebsocketResponseSerializer

    def _get_data(self, request):
        world_id = None
        display_name = None
        block_colors = {}
        creature_colors = []

        try:
            # world data
            if "world_id" in request.data:
                world_id = int(request.data["world_id"])

            # walk block/creature data just to make sure it is valid
            for key, value in request.data["config"]["world"]["blockColors"].items():
                block_colors[key] = value
            for key, value in request.data["config"]["world"]["creatureColors"].items():
                creature_colors.append((key, value))
        except Exception:  # pylint: disable=broad-except
            logger.warning(traceback.format_exc())
            return None

        logger.info("WS Post from user %s for world %s", request.user, world_id)

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
                world = World.objects.filter(
                    display_name={"name": display_name},
                    active=True,
                    owner__isnull=True,
                ).get()

        return world

    def _create_creature_colors(self, world, creature_colors, user=None):
        creature_colors_created = 0
        for creature_color in creature_colors:
            _, created = WorldCreatureColor.objects.get_or_create(
                world=world,
                creature_type=creature_color[0],
                defaults={
                    "color_data": json.dumps(creature_color[1]),
                    "uploader": user,
                },
            )

            if created:
                creature_colors_created += 1

        return creature_colors_created

    def post(self, request, *args, **kwargs):
        data = self._get_data(request)

        if data is None:
            logger.warning("Bad ingest data:\n%s", request.data)
            return Response(status=400)

        world = self._get_world(data[0], data[1])

        if world is None:
            return Response(status=425)

        block_colors_created = WorldBlockColor.objects.create_colors_from_ws(
            world, data[2], user=request.user
        )
        creature_colors_created = self._create_creature_colors(
            world, data[3], user=request.user
        )

        if block_colors_created > 0:
            recalculate_and_send_exo.delay(world.id)

        return Response(
            status=201,
            data={
                "blocks": block_colors_created,
                "creatures": creature_colors_created,
            },
        )

    post.operation_id = "ingestWebsocketData"  # type: ignore # noqa E501


class WorldControlSimpleDataView(BoundlexxGenericViewSet):
    """
    Accepts World data from the World Control.

    Requires API Key. Requires special permission to use.
    """

    permission_classes = [IsAuthenticated, IsWorldTrusted]
    serializer_class = WorldControlSimpleSerializer

    def _get_data(self, request):
        world_id = None

        try:
            if "world_id" in request.data:
                world_id = int(request.data["world_id"])

            perms = {}

            if "global_perms" in request.data:
                if "can_visit" in request.data["global_perms"]:
                    perms["can_visit"] = bool(request.data["global_perms"]["can_visit"])
                if "can_edit" in request.data["global_perms"]:
                    perms["can_edit"] = bool(request.data["global_perms"]["can_edit"])
                if "can_claim" in request.data["global_perms"]:
                    perms["can_claim"] = bool(request.data["global_perms"]["can_claim"])

            finalized = None
            if "finalized" in request.data:
                finalized = bool(request.data["finalized"])

        except Exception:  # pylint: disable=broad-except
            logger.warning(traceback.format_exc())
            return None

        logger.info("WC Post from user %s for world %s", request.user, world_id)

        if world_id is None:
            return None

        return (world_id, perms, finalized)

    def _get_world(self, world_id):
        if world_id is not None:
            world = World.objects.filter(id=world_id).first()
            if world is None:
                c = BoundlessClient()
                world_data = c.get_world_data(world_id)
                world, _ = World.objects.get_or_create_from_game_dict(
                    world_data["worldData"]
                )

        return world

    def process_data(self, request):
        data = self._get_data(request)

        if data is None:
            logger.warning("Bad ingest data:\n%s", request.data)
            return Response(status=400), None

        world = self._get_world(data[0])
        if world is None:
            return Response(status=425), None

        if world.is_sovereign:
            if "can_visit" in data[1]:
                world.is_public = data[1]["can_visit"]
            if "can_edit" in data[1]:
                world.is_public_edit = data[1]["can_edit"]
            if "can_claim" in data[1]:
                world.is_public_claim = data[1]["can_claim"]
            if data[2] is not None:
                world.is_finalized = data[2]
            world.save()

        return None, world

    def post(self, request, *args, **kwargs):
        response, _ = self.process_data(request)

        if response is None:
            response = Response(status=201)
        return response

    post.operation_id = "ingestWorldControlDataSimple"  # type: ignore # noqa E501


class WorldControlDataView(WorldControlSimpleDataView):
    """
    Accepts World data from the World Control.

    Requires API Key. Requires special permission to use.
    """

    throttle_classes = [UserRateThrottle]
    serializer_class = WorldControlSerializer

    def post(self, request, *args, **kwargs):
        response, world = self.process_data(request)

        if response is not None:
            return response

        color_data = {}
        try:
            # walk data just to make sure it is valid
            for block_id, colors in request.data["colors"].items():

                if not isinstance(colors["default"], int):
                    raise TypeError

                for color in colors["possible"]:
                    if not isinstance(color, int):
                        raise TypeError

                color_data[int(block_id)] = colors
        except Exception:  # pylint: disable=broad-except
            logger.warning("Bad ingest data:\n%s", request.data)
            return Response(status=400)

        add_world_control_data.delay(world.id, color_data, request.user.id)
        return Response(status=202)

    post.requires_processing = True  # type: ignore
    post.operation_id = "ingestWorldControlData"  # type: ignore # noqa E501


class WorldForumIDView(BoundlexxGenericViewSet):
    """
    Allows setting forum ID for a given world

    Requires API Key. Requires special permission to use.
    """

    permission_classes = [IsAuthenticated, IsWorldTrusted]
    serializer_class = WorldForumIDSerializer

    def post(self, request, *args, **kwargs):
        post = self.serializer_class(data=request.data)

        if not post.is_valid() or post.world is None:
            return Response(post.errors, status=400)

        post.world.forum_id = post.data["forum_id"]
        post.world.save()
        return Response(status=201)

    post.operation_id = "ingestWorldForumID"  # type: ignore # noqa E501
