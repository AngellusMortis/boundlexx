from django.urls import include, path
from django.views.generic import RedirectView

from boundlexx.api.common import views
from boundlexx.api.v1.router import router

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", RedirectView.as_view(url="/api/v1/"), name="go-to-default-api"),
    path("v1/", include((router.urls, "api"), namespace="v1")),
    path("ingest-ws-data/", views.WorldWSDataView.as_view()),
    path("ingest-wcsimple-data/", views.WorldControlSimpleDataView.as_view()),
    path("ingest-wc-data/", views.WorldControlDataView.as_view()),
]
