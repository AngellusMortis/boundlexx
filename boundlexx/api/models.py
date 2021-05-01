from django.db import models
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from config.storages import select_storage


class ExportedFile(ExportModelOperationsMixin("exported_file"), models.Model):  # type: ignore # noqa E501
    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.TextField()
    exported_file = models.FileField(storage=select_storage("exports"))
    last_updated = models.DateTimeField(auto_now=True)
