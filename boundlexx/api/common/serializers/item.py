from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from boundlexx.api.common.serializers.base import (
    AzureImageField,
    LocalizedNameSerializer,
    LocalizedStringSerializer,
)
from boundlexx.api.common.serializers.color import IDColorSerializer
from boundlexx.api.common.serializers.world import IDWorldSerializer
from boundlexx.boundless.models import (
    Item,
    ResourceCount,
    ResourceData,
    ResourceDataBestWorld,
    Subtitle,
)


class SubtitleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # noqa: A003
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )

    class Meta:
        model = Subtitle
        fields = ["id", "localization"]


class IDItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "game_id",
        ]


class ResourceDataSerializer(serializers.ModelSerializer):
    is_embedded = serializers.BooleanField()
    exo_only = serializers.BooleanField()

    max_tier = serializers.IntegerField(
        help_text=_("Max tier of world to be found on. Starts at 0."),
    )

    min_tier = serializers.IntegerField(
        help_text=_("Min tier of world to be found on. Starts at 0."),
    )

    best_max_tier = serializers.IntegerField(
        help_text=_("Max tier of world to be found on. Starts at 0."),
    )

    best_min_tier = serializers.IntegerField(
        help_text=_("Min tier of world to be found on. Starts at 0."),
    )

    best_world_types = serializers.ListField(
        child=serializers.ChoiceField(choices=ResourceDataBestWorld.WorldType)
    )

    shape = serializers.IntegerField()
    size_max = serializers.IntegerField()
    size_min = serializers.IntegerField()
    altitude_max = serializers.IntegerField()
    altitude_min = serializers.IntegerField()
    distance_max = serializers.IntegerField(allow_null=True)
    distance_min = serializers.IntegerField(allow_null=True)
    cave_weighting = serializers.FloatField()
    size_skew_to_min = serializers.FloatField()
    blocks_above_max = serializers.IntegerField()
    blocks_above_min = serializers.IntegerField()
    liquid_above_max = serializers.IntegerField()
    liquid_above_min = serializers.IntegerField()
    noise_frequency = serializers.FloatField(allow_null=True)
    noise_threshold = serializers.FloatField(allow_null=True)
    liquid_favorite = IDItemSerializer(allow_null=True)
    three_d_weighting = serializers.FloatField()
    surface_favorite = IDItemSerializer(allow_null=True)
    surface_weighting = serializers.FloatField()
    altitude_best_lower = serializers.IntegerField()
    altitude_best_upper = serializers.IntegerField()
    distance_best_lower = serializers.IntegerField(allow_null=True)
    distance_best_upper = serializers.IntegerField(allow_null=True)
    blocks_above_best_lower = serializers.IntegerField()
    blocks_above_best_upper = serializers.IntegerField()
    liquid_above_best_upper = serializers.IntegerField()
    liquid_above_best_lower = serializers.IntegerField()
    liquid_second_favorite = IDItemSerializer(allow_null=True)
    surface_second_favorite = IDItemSerializer(allow_null=True)

    class Meta:
        model = ResourceData
        fields = [
            "is_embedded",
            "exo_only",
            "max_tier",
            "min_tier",
            "best_world_types",
            "best_max_tier",
            "best_min_tier",
            "shape",
            "size_max",
            "size_min",
            "altitude_max",
            "altitude_min",
            "distance_max",
            "distance_min",
            "cave_weighting",
            "size_skew_to_min",
            "blocks_above_max",
            "blocks_above_min",
            "liquid_above_max",
            "liquid_above_min",
            "noise_frequency",
            "noise_threshold",
            "liquid_favorite",
            "three_d_weighting",
            "surface_favorite",
            "surface_weighting",
            "altitude_best_lower",
            "altitude_best_upper",
            "distance_best_lower",
            "distance_best_upper",
            "blocks_above_best_lower",
            "blocks_above_best_upper",
            "liquid_above_best_upper",
            "liquid_above_best_lower",
            "liquid_second_favorite",
            "surface_second_favorite",
        ]


class SimpleItemSerializer(IDItemSerializer):
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )

    item_subtitle = SubtitleSerializer()
    list_type = LocalizedStringSerializer()
    has_colors = serializers.BooleanField()
    default_color = IDColorSerializer(allow_null=True)
    has_metal_variants = serializers.BooleanField()
    has_world_colors = serializers.BooleanField()
    is_resource = serializers.BooleanField()
    image_url = AzureImageField(source="image", allow_null=True)

    class Meta:
        model = Item
        fields = [
            "game_id",
            "name",
            "string_id",
            "image_url",
            "has_colors",
            "has_metal_variants",
            "has_world_colors",
            "default_color",
            "localization",
            "item_subtitle",
            "list_type",
            "is_resource",
        ]


class ItemSerializer(SimpleItemSerializer):
    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    description = LocalizedStringSerializer()

    mint_value = serializers.FloatField()
    max_stack = serializers.IntegerField()
    prestige = serializers.IntegerField()
    mine_xp = serializers.IntegerField()
    build_xp = serializers.IntegerField()
    is_liquid = serializers.BooleanField()
    is_block = serializers.BooleanField()
    resource_data = ResourceDataSerializer(allow_null=True)

    class Meta:
        model = Item
        fields = [
            "game_id",
            "name",
            "string_id",
            "image_url",
            "has_colors",
            "has_metal_variants",
            "has_world_colors",
            "default_color",
            "next_request_basket_update",
            "next_shop_stand_update",
            "localization",
            "item_subtitle",
            "mint_value",
            "max_stack",
            "prestige",
            "mine_xp",
            "build_xp",
            "list_type",
            "description",
            "is_resource",
            "is_block",
            "is_liquid",
            "resource_data",
        ]


class ItemResourceCountSerializer(serializers.ModelSerializer):
    world = IDWorldSerializer(source="world_poll.world")
    average_per_chunk = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = ResourceCount
        fields = [
            "world",
            "is_embedded",
            "percentage",
            "count",
            "average_per_chunk",
        ]
