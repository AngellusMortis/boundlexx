from django.urls import include, path
from django.views.generic import RedirectView

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
router.register(r"worlds", views.WorldViewSet, basename="world")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", RedirectView.as_view(url="/api/v1/"), name="go-to-default-api"),
    path("v1/", include((router.urls, "api"), namespace="v1")),
]
