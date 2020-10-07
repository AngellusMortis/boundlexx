from typing import Optional

from rest_framework import serializers

from boundlexx.boundless.models import World

BASE_QUERY = World.objects.all().select_related("assignment")


class NullSerializer(serializers.Serializer):
    def create(self, validated_data):
        return

    def update(self, instance, validated_data):
        return


class ForumFormatPostSerialzier(NullSerializer):
    username = serializers.CharField(
        required=False,
        help_text="Your Boundless Username. Required for Sovereign worlds.",
    )
    world_id = serializers.IntegerField(
        required=True,
        help_text=(
            "The ID of your world if 'World Name' is not working. You can get "
            'your World ID from the <a href="https://forum.playboundless.com/'
            "uploads/default/original/3X/3/f/3fef2e21cedc3d4594971d6143d40110bd489686"
            '.jpeg" target="_blank">Debug Menu</a> if you are on PC'
        ),
        label="World ID",
    )
    will_renew = serializers.NullBooleanField(
        required=False,
        help_text="Do you plan to renew this world? Required for Sovereign worlds.",
        label="Will Renew?",
    )
    compactness = serializers.NullBooleanField(
        required=False,
        help_text="Is Beacon compactness enabled?",
        label="Beacon Compactness?",
    )
    can_visit = serializers.BooleanField(
        required=False,
        help_text=(
            "Can Everyone warp/use portals to your world? "
            "Required for Sovereign worlds."
        ),
        label="Can Visit?",
    )
    can_edit = serializers.BooleanField(
        required=False,
        help_text=(
            "Can Everyone edit blocks on your world (outside of plots)?"
            " Required for Sovereign worlds."
        ),
        label="Can Edit?",
    )
    can_claim = serializers.BooleanField(
        required=False,
        help_text=(
            "Can Everyone create beacon and plot on your world? "
            "Required for Sovereign worlds."
        ),
        label="Can Claim?",
    )
    portal_directions = serializers.CharField(
        required=False,
        max_length=100,
        help_text=(
            "Directions to help players find the portal to your world."
            "Required for Sovereign worlds."
        ),
        label="Portal Directions",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world: Optional[World] = None

    def validate_world_id(self, value):
        try:
            world = BASE_QUERY.get(pk=value)
        except World.DoesNotExist:
            raise serializers.ValidationError(  # pylint: disable=raise-missing-from
                "Could not find a world with that ID"
            )
        else:
            self.world = world

        return value

    def validate(self, attrs):
        if self.world.is_sovereign:  # type: ignore
            errors = {}
            for key in [
                "username",
                "will_renew",
                "portal_directions",
                "can_visit",
                "can_edit",
                "can_claim",
            ]:
                if key not in attrs:
                    errors[key] = "Required if Sovereign world"
            if len(errors) > 0:
                raise serializers.ValidationError(errors)

        return attrs


class ForumFormatSerialzier(NullSerializer):
    title = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True)
