from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import FormView

from boundlexx.api.forms import ForumFormatForm
from boundlexx.notifications.models import WorldNotification


class ForumFormatView(FormView):
    template_name = "boundlexx/forum_format.html"
    form_class = ForumFormatForm

    def form_valid(self, form):
        world = form.cleaned_data["world"]
        resources = None
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

        if world.worldpoll_set.count() > 0:
            resources = (
                world.worldpoll_set.prefetch_related("resourcecount_set")
                .first()
                .resources.order_by("-count")
                .select_related("item")
            )

        _, title, body = WorldNotification().forum(world, resources, extra=extra)

        return HttpResponse(
            render(
                self.request,
                "boundlexx/forum_output.html",
                context={"title": title, "body": body},
            ),
        )
