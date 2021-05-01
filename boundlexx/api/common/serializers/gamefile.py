from django.utils.translation import gettext as _
from rest_framework import serializers

from boundlexx.ingest.models import GameFile


class SimpleGameFileSerializer(serializers.ModelSerializer):
    file_type = serializers.ChoiceField(
        source="get_file_type_display",
        help_text=_("`0` = JSON, `1` = MSGPACK, `2` = OTHER"),
        choices=GameFile.Filetype.choices,
    )

    class Meta:
        model = GameFile
        fields = [
            "id",
            "folder",
            "filename",
            "file_type",
            "game_version",
        ]


class GameFileSerializer(SimpleGameFileSerializer):
    class Meta:
        model = GameFile
        fields = [
            "id",
            "folder",
            "filename",
            "file_type",
            "game_version",
            "content",
        ]
