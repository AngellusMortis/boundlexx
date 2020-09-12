from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from boundlexx.ingest.models import GameFile


@admin.register(GameFile)
class GameFileAdmin(admin.ModelAdmin):
    search_fields = ["filepath"]

    list_filter = [
        "file_type",
        "folder",
    ]

    list_display = [
        "filepath",
        "folder",
        "filename",
        "file_type",
        "game_version",
    ]
    readonly_fields = [
        "folder",
        "filename",
        "file_type",
        "game_version",
    ]

    formfield_overrides = {
        fields.JSONField: {"widget": JSONEditorWidget},
    }
