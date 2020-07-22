from .site import BGEAdminSite

__all__ = ["BGEAdminSite", "ADMIN_APPS"]

ADMIN_APPS = (
    "django.contrib.*",
    "bge.users.*",
    "allauth.*",
    "oidc_provider.*",
)
