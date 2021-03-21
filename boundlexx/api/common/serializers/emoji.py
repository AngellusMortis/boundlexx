from rest_framework import serializers

from boundlexx.api.common.serializers.base import AzureImageField
from boundlexx.boundless.models import Emoji


class EmojiSerializer(serializers.ModelSerializer):
    names = serializers.ListField(child=serializers.CharField())
    category = serializers.ChoiceField(choices=Emoji.EmojiCategory)
    image_url = AzureImageField(source="image", allow_null=True)

    class Meta:
        model = Emoji
        fields = [
            "names",
            "category",
            "image_url",
        ]
