from typing import Any
from urllib.parse import urlencode

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import FormView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from boundlexx.api.common.serializers import (
    ForumFormatPostSerialzier,
    ForumFormatSerialzier,
)
from boundlexx.api.forms import ForumFormatForm
from boundlexx.api.schemas import DescriptiveAutoSchema
from boundlexx.notifications.models import WorldNotification


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


class ForumFormatAPIView(GenericViewSet):
    schema = DescriptiveAutoSchema(tags=["Misc."])

    permission_classes = [AllowAny]
    serializer_class = ForumFormatPostSerialzier
    response_serializer = ForumFormatSerialzier
    authentication_classes: list[Any] = []

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
                    "forum_links": post.data["forum_links"],
                }
            else:
                extra = {}

            if post.data["update_link"]:
                params = {
                    "world_id": post.world.id,
                    "update_link": "true",
                }

                if post.world.is_sovereign:
                    if post.data["can_visit"] is not None:
                        params["can_visit"] = str(post.data["can_visit"]).lower()

                    if post.data["can_edit"] is not None:
                        params["can_edit"] = str(post.data["can_visit"]).lower()

                    if post.data["can_claim"] is not None:
                        params["can_claim"] = str(post.data["can_claim"]).lower()

                    if post.data["compactness"] is not None:
                        params["compactness"] = str(post.data["can_visit"]).lower()

                    if post.data["portal_directions"] is not None:
                        params["portal_directions"] = post.data["portal_directions"]

                    if post.data["username"] is not None:
                        params["username"] = post.data["username"]

                    if post.data["will_renew"] is not None:
                        params["will_renew"] = str(post.data["will_renew"]).lower()

                extra.update(
                    {
                        "update_link": "https://www.boundlexx.app/tools/forum/?"
                        + urlencode(params)
                    }
                )

            title, body = get_response(post.world, extra)
            return Response({"title": title, "body": body})
        return Response(post.errors, status=400)

    post.operation_id = "createForumTemplate"  # type: ignore # noqa E501


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
