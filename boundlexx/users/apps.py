from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "boundlexx.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            # pylint: disable=unused-import,import-outside-toplevel
            import boundlexx.users.signals  # noqa
        except ImportError:
            pass
