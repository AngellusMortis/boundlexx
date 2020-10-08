from rest_framework import serializers

from boundlexx.api.common.serializers.base import AzureImageField
from boundlexx.boundless.models import Emoji


class EmojiSerializer(serializers.ModelSerializer):
    image_url = AzureImageField(source="image", allow_null=True)
    names = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Emoji
        fields = [
            "names",
            "image_url",
        ]
