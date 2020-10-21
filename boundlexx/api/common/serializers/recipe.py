from rest_framework import serializers

from boundlexx.api.common.serializers.base import LocalizedStringSerializer
from boundlexx.api.common.serializers.item import IDItemSerializer
from boundlexx.api.common.serializers.skill import IDSkillSerializer
from boundlexx.boundless.models import (
    Recipe,
    RecipeGroup,
    RecipeInput,
    RecipeLevel,
    RecipeRequirement,
)


class IDRecipeGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # noqa: A003

    class Meta:
        model = RecipeGroup
        fields = [
            "id",
        ]


class RecipeGroupSerializer(serializers.ModelSerializer):
    display_name = LocalizedStringSerializer()
    members = IDItemSerializer(many=True)

    class Meta:
        model = RecipeGroup
        fields = [
            "id",
            "name",
            "display_name",
            "members",
        ]


class RecipeRequirementSerializer(serializers.ModelSerializer):
    skill = IDSkillSerializer()

    class Meta:
        model = RecipeRequirement
        fields = [
            "skill",
            "level",
        ]


class RecipeInputSerializer(serializers.ModelSerializer):
    group = IDRecipeGroupSerializer(allow_null=True)
    item = IDItemSerializer(allow_null=True)

    class Meta:
        model = RecipeInput
        fields = [
            "group",
            "item",
            "count",
        ]


class RecipeLevelSerializer(serializers.ModelSerializer):
    inputs = RecipeInputSerializer(many=True)

    class Meta:
        model = RecipeLevel
        fields = [
            "level",
            "wear",
            "spark",
            "duration",
            "output_quantity",
            "inputs",
        ]


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # noqa: A003
    output = IDItemSerializer()
    requirements = RecipeRequirementSerializer(many=True)
    tints = IDItemSerializer(many=True)
    levels = RecipeLevelSerializer(many=True)
    machine = serializers.ChoiceField(
        required=False, choices=Recipe.MachineType.choices
    )
    machine_level = serializers.ChoiceField(
        required=False, choices=Recipe.MachineLevelType.choices
    )
    required_event = serializers.ChoiceField(
        required=False, choices=Recipe.EventType.choices
    )
    required_backer_tier = serializers.IntegerField(allow_null=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "heat",
            "craft_xp",
            "machine",
            "output",
            "can_hand_craft",
            "machine_level",
            "power",
            "group_name",
            "knowledge_unlock_level",
            "tints",
            "requirements",
            "levels",
            "required_event",
            "required_backer_tier",
        ]
