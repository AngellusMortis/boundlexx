from django.urls import include, path
from django.views.generic import TemplateView

from boundlexx.api import views
from boundlexx.api.routers import APIDocsRouter

router = APIDocsRouter()
router.register(r"colors", views.ColorViewSet, basename="color")
router.register(r"items", views.ItemViewSet, basename="item").register(
    r"resource-counts",
    views.ItemResourceCountViewSet,
    basename="item-resource-count",
    parents_query_lookups=["item__game_id"],
)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="boundlexx/api/docs.html"),
        name="api-docs",
    ),
    path("v1/", include((router.urls, "api"), namespace="v1")),
]
