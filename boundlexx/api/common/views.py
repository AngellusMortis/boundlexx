import json
import logging
import traceback
from typing import Any, List

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import FormView
from rest_framework import views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from boundlexx.api.common.serializers import (
    ForumFormatPostSerialzier,
    ForumFormatSerialzier,
)
from boundlexx.api.forms import ForumFormatForm
from boundlexx.boundless.client import BoundlessClient
from boundlexx.boundless.models import World, WorldBlockColor, WorldCreatureColor
from boundlexx.boundless.tasks import add_world_control_data, recalculate_colors
from boundlexx.notifications.models import ExoworldNotification, WorldNotification

logger = logging.getLogger("ingest")


def get_response(world, extra):
    resources = None

    if world.worldpoll_set.count() > 0:
        resources = (
            world.worldpoll_set.prefetch_related("resourcecount_set")
            .first()
            .resources.order_by("-count")
            .select_related("item")
        )

    _, title, body = WorldNotification().forum(world, resources, extra=extra)

    return title, body


class ForumFormatAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ForumFormatPostSerialzier
    response_serializer = ForumFormatSerialzier
    authentication_classes: List[Any] = []

    def post(self, request):
        post = self.serializer_class(data=request.data)

        if post.is_valid() and post.world is not None:
            if post.world.is_sovereign:
                extra = {
                    "perms": {
                        "can_visit": post.data["can_visit"],
                        "can_edit": post.data["can_edit"],
                        "can_claim": post.data["can_claim"],
                    },
                    "compactness": post.data.get("compactness"),
                    "directions": post.data.get("portal_directions"),
                    "username": post.data["username"],
                    "will_renew": post.data["will_renew"],
                }
            else:
                extra = {}

            title, body = get_response(post.world, extra)
            return Response({"title": title, "body": body})
        return Response(post.errors, status=400)


class ForumFormatView(FormView):
    template_name = "boundlexx/forum_format.html"
    form_class = ForumFormatForm

    def form_valid(self, form):
        world = form.cleaned_data["world"]
        extra = {
            "perms": {
                "can_visit": form.cleaned_data["can_visit"],
                "can_edit": form.cleaned_data["can_edit"],
                "can_claim": form.cleaned_data["can_claim"],
            },
            "compactness": form.cleaned_data["compactness"],
            "directions": form.cleaned_data["portal_directions"],
            "username": form.cleaned_data["username"],
            "will_renew": form.cleaned_data["will_renew"],
        }

        title, body = get_response(world, extra)

        return HttpResponse(
            render(
                self.request,
                "boundlexx/forum_output.html",
                context={"title": title, "body": body},
            ),
        )


class WorldWSDataView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_data(self, request):
        world_id = None
        display_name = None
        block_colors = {}
        creature_colors = []

        try:
            # world data
            if "world_id" in request.data:
                world_id = int(request.data["world_id"])
            elif "display_name" in request.data:
                display_name = request.data["display_name"]
            else:
                display_name = request.data.get("config", {}).get("displayName")

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
            recalculate_colors.delay([world.id])
            if world.owner is None:
                ExoworldNotification.objects.send_update_notification(world)

        return Response(
            status=200,
            data={
                "blocks": block_colors_created,
                "creatures": creature_colors_created,
            },
        )


class WorldControlSimpleDataView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_data(self, request):
        world_id = None

        try:
            if "world_id" in request.data:
                world_id = int(request.data["world_id"])

            # force eval permission data to verify it
            perms = {
                "can_visit": bool(request.data["global_perms"]["can_visit"]),
                "can_edit": bool(request.data["global_perms"]["can_edit"]),
                "can_claim": bool(request.data["global_perms"]["can_claim"]),
            }

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

        world.is_public = data[1]["can_visit"]
        world.is_public_edit = data[1]["can_edit"]
        world.is_public_claim = data[1]["can_claim"]
        world.is_finalized = data[2]
        world.save()

        return None, world

    def post(self, request, *args, **kwargs):
        response, _ = self.process_data(request)

        if response is None:
            response = Response(status=200)
        return response


class WorldControlDataView(WorldControlSimpleDataView):
    throttle_classes = [UserRateThrottle]

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
        return Response(status=200)
