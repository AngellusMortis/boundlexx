from django.contrib.admin.apps import AdminConfig


class BoundlexxAdminConfig(AdminConfig):
    default_site = "boundlexx.admin.BoundlexxAdminSite"
