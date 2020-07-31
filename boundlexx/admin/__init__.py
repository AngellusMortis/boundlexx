from .site import BoundlexxAdminSite

__all__ = ["BoundlexxAdminSite", "ADMIN_APPS"]

ADMIN_APPS = (
    "django.contrib.*",
    "boundlexx.users.*",
    "rest_framework.authtoken.*",
)
