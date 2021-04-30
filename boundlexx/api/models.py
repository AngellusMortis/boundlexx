from django.db import models
from django.utils.translation import gettext_lazy as _

from config.storages import select_storage


class ExportedFile(models.Model):
    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.TextField()
    exported_file = models.FileField(storage=select_storage("exports"))
    last_updated = models.DateTimeField(auto_now=True)
