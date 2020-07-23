from django.conf import settings
from django.contrib.sites.models import Site
from django.db.utils import ProgrammingError
from django.urls import include, path
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from bge.api import views

router = routers.DefaultRouter()
router.register(r"color", views.ColorViewSet)
router.register(r"item", views.ItemViewSet)


def get_site():
    try:
        return Site.objects.get_current()
    except ProgrammingError:
        return "example.com"


schema_view = get_schema_view(
    title="Boundless Grand Exchange",
    description="BGE API",
    version="0.0.1",
    url=f"{settings.API_PROTOCOL}://{get_site()}/{settings.API_BASE}",
    urlconf="bge.api.urls",
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
]
