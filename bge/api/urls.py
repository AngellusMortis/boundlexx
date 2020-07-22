from django.urls import include, path
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from bge.api import views

router = routers.DefaultRouter()
router.register(r"color", views.ColorViewSet)

schema_view = get_schema_view(
    title="Boundless Grand Exchange",
    description="BGE API",
    version="0.0.1",
    url="http://localhost:9000/api/",
    urlconf="bge.api.urls",
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
]
