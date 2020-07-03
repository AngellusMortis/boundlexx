from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "bge.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            # pylint: disable=unused-import,import-outside-toplevel
            import bge.users.signals  # noqa
        except ImportError:
            pass
