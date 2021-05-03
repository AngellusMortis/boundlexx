from rest_framework import serializers

from boundlexx.api.common.serializers.base import NullSerializer, WorldIDPostSerializer


class ForumFormatPostSerializer(WorldIDPostSerializer):
    username = serializers.CharField(
        required=False,
        help_text="Your Boundless Username. Required for Sovereign worlds.",
    )
    will_renew = serializers.BooleanField(
        allow_null=True,
        required=False,
        help_text="Do you plan to renew this world? Required for Sovereign worlds.",
        label="Will Renew?",
    )
    compactness = serializers.BooleanField(
        allow_null=True,
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
        max_length=2000,
        help_text=(
            "Directions to help players find the portal to your world."
            "Required for Sovereign worlds."
        ),
        label="Portal Directions",
    )
    update_link = serializers.BooleanField(
        required=False,
        default=True,
        help_text=("Add update link to easily update the template?"),
        label="Add Update Link",
    )
    forum_links = serializers.BooleanField(
        required=False,
        default=True,
        help_text=("Use Boundless Forum links for images?"),
        label="Boundless Forum Links",
    )

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


class ForumFormatSerializer(NullSerializer):
    title = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True)
