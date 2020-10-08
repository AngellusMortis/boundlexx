from typing import Any, List

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import FormView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from boundlexx.api.common.serializers import (
    ForumFormatPostSerialzier,
    ForumFormatSerialzier,
)
from boundlexx.api.forms import ForumFormatForm
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
