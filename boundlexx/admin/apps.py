from django.contrib.admin.apps import AdminConfig as _BaseAdminConfig

__all__ = ["BoundlexxAdminConfig"]


class BoundlexxAdminConfig(_BaseAdminConfig):
    default_site = "boundlexx.admin.BoundlexxAdminSite"
