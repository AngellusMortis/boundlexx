from django.contrib.admin.apps import AdminConfig


class BGEAdminConfig(AdminConfig):
    default_site = "bge.admin.BGEAdminSite"
