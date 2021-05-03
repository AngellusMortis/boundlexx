from django.utils.translation import gettext as _
from rest_framework import serializers

from boundlexx.api.common.serializers.color import IDColorSerializer
from boundlexx.api.common.serializers.item import IDItemSerializer
from boundlexx.api.common.serializers.world import IDWorldSerializer
from boundlexx.boundless.models import WorldBlockColor


class BaseWBCSerializer(serializers.ModelSerializer):
    color = IDColorSerializer()
    item = IDItemSerializer()
    world = IDWorldSerializer()

    active = serializers.BooleanField(
        help_text=_("Is this the current color for the world?")
    )
    is_new = serializers.BooleanField(
        help_text=_(
            "Is this the first time the color has been seen (only Homeworld/Sovereign)?"
        )
    )
    is_new_exo = serializers.BooleanField(
        help_text=_("Is this the first time the color has been seen (including Exo)?")
    )
    is_default = serializers.BooleanField(
        help_text=_("Is this the color the world spawned with?")
    )
    is_perm = serializers.BooleanField(
        help_text=_("Does this color exist on a Homeworld?")
    )
    is_sovereign_only = serializers.BooleanField(
        help_text=_("Is this color only on Sovereigns (and not Homeworlds)?")
    )
    is_new_transform = serializers.BooleanField(
        help_text=_(
            (
                "Is this the first time the color has been seen (including "
                "recipe transforms)?"
            )
        )
    )
    is_exo_only = serializers.BooleanField(
        help_text=_("Is this color an Exoworld only color?")
    )
    days_since_exo = serializers.IntegerField(
        allow_null=True, help_text=_("Days since last Exoworld that had this color")
    )
    days_since_transform_exo = serializers.IntegerField(
        allow_null=True,
        help_text=_(
            "Days since last Exoworld had this color (including recipe transforms)"
        ),
    )
    first_world = IDWorldSerializer(
        allow_null=True, help_text=_("First world that had this color")
    )
    last_exo = IDWorldSerializer(
        allow_null=True, help_text=_("Last Exoworld that had this color")
    )
    transform_first_world = IDWorldSerializer(
        allow_null=True,
        help_text=_("First world that had this color (including recipe transforms)"),
    )
    transform_last_exo = IDWorldSerializer(
        allow_null=True,
        help_text=_("Last Exoworld that had this color (including recipe transforms)"),
    )


class PossibleWBCSerializer(BaseWBCSerializer):
    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
        ]


class PossibleItemWBCSerializer(BaseWBCSerializer):
    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
        ]


class WorldBlockColorSerializer(BaseWBCSerializer):
    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
            "color",
            "active",
            "is_default",
            "is_perm",
            "is_sovereign_only",
            "is_exo_only",
            "is_new",
            "is_new_exo",
            "is_new_transform",
            "days_since_exo",
            "days_since_transform_exo",
            "first_world",
            "last_exo",
            "transform_first_world",
            "transform_last_exo",
        ]


class BlockColorSerializer(BaseWBCSerializer):
    class Meta:
        model = WorldBlockColor
        fields = [
            "item",
            "world",
            "active",
            "is_default",
            "is_perm",
            "is_sovereign_only",
            "is_exo_only",
            "is_new",
            "is_new_exo",
            "is_new_transform",
            "days_since_exo",
            "days_since_transform_exo",
            "first_world",
            "last_exo",
            "transform_first_world",
            "transform_last_exo",
        ]


class ItemColorSerializer(BaseWBCSerializer):
    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
            "active",
            "is_default",
            "is_perm",
            "is_sovereign_only",
            "is_exo_only",
            "is_new",
            "is_new_exo",
            "is_new_transform",
            "days_since_exo",
            "days_since_transform_exo",
            "first_world",
            "last_exo",
            "transform_first_world",
            "transform_last_exo",
        ]


class WorldColorSerializer(BaseWBCSerializer):
    class Meta:
        model = WorldBlockColor
        fields = [
            "color",
            "world",
            "active",
            "is_default",
            "is_perm",
            "is_sovereign_only",
            "is_exo_only",
            "is_new",
            "is_new_exo",
            "is_new_transform",
            "days_since_exo",
            "days_since_transform_exo",
            "first_world",
            "last_exo",
            "transform_first_world",
            "transform_last_exo",
        ]
