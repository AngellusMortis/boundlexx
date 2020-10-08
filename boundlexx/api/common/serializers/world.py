from django.utils.translation import ugettext as _
from rest_framework import serializers

from boundlexx.api.common.serializers.base import AzureImageField, NullSerializer
from boundlexx.api.common.serializers.skill import IDSkillSerializer
from boundlexx.boundless.models import World


class IDWorldSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # noqa: A003

    class Meta:
        model = World
        fields = [
            "id",
        ]


class SimpleWorldSerializer(IDWorldSerializer):
    id = serializers.IntegerField()  # noqa: A003
    active = serializers.BooleanField(
        help_text=_("Does this world still exist (returned by game API)?")
    )
    image_url = AzureImageField(source="image", allow_null=True)
    text_name = serializers.CharField(allow_null=True, required=True)
    html_name = serializers.CharField(allow_null=True, required=True)
    tier = serializers.IntegerField(help_text=_("Tier of the world. Starts at 0."))
    size = serializers.IntegerField()
    world_type = serializers.ChoiceField(choices=World.WorldType.choices)
    special_type = serializers.IntegerField(
        allow_null=True, help_text=_("`1` = Color-Cycling")
    )
    is_sovereign = serializers.BooleanField()
    is_perm = serializers.BooleanField()
    is_exo = serializers.BooleanField()
    is_creative = serializers.BooleanField()
    is_locked = serializers.BooleanField()

    class Meta:
        model = World
        fields = [
            "id",
            "active",
            "image_url",
            "display_name",
            "text_name",
            "html_name",
            "tier",
            "size",
            "world_type",
            "special_type",
            "is_sovereign",
            "is_perm",
            "is_exo",
            "is_creative",
            "is_locked",
        ]


class BowSerializer(NullSerializer):
    best = serializers.ListField(child=serializers.CharField())
    neutral = serializers.ListField(child=serializers.CharField())
    lucent = serializers.ListField(child=serializers.CharField())


class WorldSerializer(serializers.ModelSerializer):
    assignment = IDWorldSerializer(allow_null=True)

    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    id = serializers.IntegerField()  # noqa: A003
    active = serializers.BooleanField()
    name = serializers.CharField()
    text_name = serializers.CharField(allow_null=True)
    html_name = serializers.CharField(allow_null=True)
    address = serializers.CharField()
    image_url = AzureImageField(source="image", allow_null=True)
    forum_url = serializers.URLField(allow_null=True)
    tier = serializers.IntegerField(help_text=_("Tier of the world. Starts at 0."))
    size = serializers.IntegerField(
        help_text=_("`192` = 3km world, `288` = 4.5km world, `384` = 6km world")
    )
    time_offset = serializers.DateTimeField(allow_null=True)
    world_type = serializers.ChoiceField(choices=World.WorldType.choices)
    region = serializers.ChoiceField(choices=World.Region.choices)
    special_type = serializers.IntegerField(
        allow_null=True, help_text=_("`1` = Color-Cycling")
    )
    is_sovereign = serializers.BooleanField()
    is_perm = serializers.BooleanField()
    is_exo = serializers.BooleanField()
    is_creative = serializers.BooleanField()
    is_locked = serializers.BooleanField()
    is_public = serializers.BooleanField()
    is_public_edit = serializers.BooleanField(allow_null=True)
    is_public_claim = serializers.BooleanField(allow_null=True)
    is_finalized = serializers.BooleanField(allow_null=True)
    number_of_regions = serializers.IntegerField()
    start = serializers.DateTimeField(allow_null=True)
    end = serializers.DateTimeField(allow_null=True)
    surface_liquid = serializers.CharField()
    core_liquid = serializers.CharField()
    atmosphere_color = serializers.CharField()
    water_color = serializers.CharField()

    bows = BowSerializer()

    protection_points = serializers.IntegerField(
        allow_null=True,
        help_text=_(
            "'points' are not equal to levels in skill. For more details see "
            '<a href="https://forum.playboundless.com/t/28068/4">this forum '
            "post</a>."
        ),
    )
    protection_skill = IDSkillSerializer()

    class Meta:
        model = World
        fields = [
            "id",
            "active",
            "name",
            "display_name",
            "text_name",
            "html_name",
            "address",
            "image_url",
            "forum_url",
            "assignment",
            "region",
            "tier",
            "size",
            "world_type",
            "special_type",
            "protection_points",
            "protection_skill",
            "time_offset",
            "is_sovereign",
            "is_perm",
            "is_exo",
            "is_creative",
            "is_locked",
            "is_public",
            "is_public_edit",
            "is_public_claim",
            "is_finalized",
            "number_of_regions",
            "start",
            "end",
            "atmosphere_color",
            "water_color",
            "surface_liquid",
            "core_liquid",
            "bows",
            "next_request_basket_update",
            "next_shop_stand_update",
        ]
