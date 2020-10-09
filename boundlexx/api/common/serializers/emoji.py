from rest_framework import serializers

from boundlexx.api.common.serializers.base import AzureImageField
from boundlexx.boundless.models import Emoji


class EmojiSerializer(serializers.ModelSerializer):
    names = serializers.ListField(child=serializers.CharField())
    is_boundless_only = serializers.BooleanField()
    image_url = AzureImageField(source="image", allow_null=True)

    class Meta:
        model = Emoji
        fields = [
            "names",
            "is_boundless_only",
            "image_url",
        ]
