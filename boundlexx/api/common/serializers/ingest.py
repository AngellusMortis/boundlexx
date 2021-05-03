from rest_framework import serializers

from boundlexx.api.common.serializers.base import NullSerializer, WorldIDPostSerializer


class WebsocketSerializer(WorldIDPostSerializer):
    config = NullSerializer(help_text="World config object from Websocket")


class WebsocketResponseSerializer(NullSerializer):
    blocks = serializers.IntegerField()
    creatures = serializers.IntegerField()


class PermissionsSerializer(NullSerializer):
    can_visit = serializers.BooleanField()
    can_edit = serializers.BooleanField()
    can_claim = serializers.BooleanField()


class WorldControlSimpleSerializer(WorldIDPostSerializer):
    finalized = serializers.BooleanField()
    global_perms = PermissionsSerializer()


class PossibleColorSerializer(NullSerializer):
    default = serializers.IntegerField()
    possible = serializers.ListField(child=serializers.IntegerField())


class WorldControlSerializer(WorldControlSimpleSerializer):
    colors = PossibleColorSerializer()


class WorldForumIDSerializer(WorldIDPostSerializer):
    forum_id = serializers.IntegerField()
