import os

from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin


class GameFile(ExportModelOperationsMixin("game_file"), models.Model):  # type: ignore
    class Filetype(models.IntegerChoices):
        JSON = 0, "JSON"
        MSGPACK = 1, "MSGPACK"
        OTHER = 2, "OTHER"

    folder = models.CharField(
        _("Folder"),
        max_length=128,
        help_text=_("Folder relative to root of game"),
        db_index=True,
    )
    filename = models.CharField(_("Filename"), max_length=64, db_index=True)
    file_type = models.PositiveSmallIntegerField(
        _("Source File Type"),
        choices=Filetype.choices,
        db_index=True,
    )
    game_version = models.CharField(
        _("Source Game Version"),
        max_length=8,
        help_text=_("Version of the game file was ingest from"),
        db_index=True,
    )
    content = JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        unique_together = (
            "folder",
            "filename",
            "game_version",
        )

    @property
    def filepath(self):
        return os.path.join(self.folder, self.filename)
