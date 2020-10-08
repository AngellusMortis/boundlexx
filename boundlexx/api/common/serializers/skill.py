from rest_framework import serializers

from boundlexx.api.common.serializers.base import (
    AzureImageField,
    LocalizedStringSerializer,
)
from boundlexx.boundless.models import Skill, SkillGroup


class IDSkillGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # noqa: A003

    class Meta:
        model = SkillGroup
        fields = [
            "id",
        ]


class SkillGroupSerializer(IDSkillGroupSerializer):
    display_name = LocalizedStringSerializer()

    class Meta:
        model = SkillGroup
        fields = [
            "id",
            "name",
            "skill_type",
            "display_name",
            "unlock_level",
        ]


class IDSkillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # noqa: A003

    class Meta:
        model = Skill
        fields = [
            "id",
        ]


class SkillSerializer(IDSkillSerializer):
    group = IDSkillGroupSerializer()
    display_name = LocalizedStringSerializer()
    description = LocalizedStringSerializer()
    icon_url = AzureImageField(source="icon", allow_null=True)

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "display_name",
            "icon_url",
            "description",
            "group",
            "number_unlocks",
            "cost",
            "order",
            "category",
            "link_type",
            "bundle_prefix",
            "affected_by_other_skills",
        ]
