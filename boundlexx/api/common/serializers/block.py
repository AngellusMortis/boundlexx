from rest_framework import serializers

from boundlexx.api.common.serializers.item import IDItemSerializer
from boundlexx.boundless.models import Block


class BlockSerializer(serializers.ModelSerializer):
    item = IDItemSerializer(source="block_item")

    class Meta:
        model = Block
        fields = [
            "game_id",
            "name",
            "item",
        ]
