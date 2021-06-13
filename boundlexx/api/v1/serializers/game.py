from rest_framework import serializers

from boundlexx.api.common.serializers import (
    BlockSerializer,
    ColorSerializer,
    EmojiSerializer,
    IDRecipeGroupSerializer,
    ItemRequestBasketPriceSerializer,
    ItemResourceCountSerializer,
    ItemSerializer,
    ItemShopStandPriceSerializer,
    MetalSerializer,
    RecipeGroupSerializer,
    RecipeInputSerializer,
    RecipeLevelSerializer,
    RecipeRequirementSerializer,
    RecipeSerializer,
    SkillGroupSerializer,
    SkillSerializer,
    WorldRequestBasketPriceSerializer,
    WorldShopStandPriceSerializer,
)
from boundlexx.api.v1.serializers.base import (
    ItemColorsLinkField,
    NestedHyperlinkedIdentityField,
    ResourceCountLinkField,
    SovereignColorsLinkField,
    URLSimpleItemSerializer,
    URLSimpleSkillGroupSerializer,
    URLSimpleSkillSerializer,
    URLSimpleWorldSerializer,
)
from boundlexx.boundless.models import (
    Block,
    Color,
    Emoji,
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    Metal,
    Recipe,
    RecipeGroup,
    RecipeInput,
    RecipeLevel,
    RecipeRequirement,
    ResourceCount,
    Skill,
    SkillGroup,
)


class URLColorSerializer(ColorSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="color-detail",
        lookup_field="game_id",
        read_only=True,
    )
    blocks_url = serializers.HyperlinkedIdentityField(
        view_name="color-blocks-list",
        lookup_field="game_id",
        lookup_url_kwarg="color__game_id",
        read_only=True,
    )

    class Meta:
        model = Color
        fields = [
            "url",
            "blocks_url",
            "game_id",
            "base_color",
            "gleam_color",
            "localization",
            "shade",
            "base",
            "group",
        ]


class URLMetalSerializer(MetalSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="metal-detail",
        lookup_field="game_id",
        read_only=True,
    )

    class Meta:
        model = Metal
        fields = [
            "url",
            "game_id",
            "localization",
        ]


class URLItemSerializer(ItemSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="item-detail",
        lookup_field="game_id",
        read_only=True,
    )
    resource_counts_url = ResourceCountLinkField()
    request_baskets_url = serializers.HyperlinkedIdentityField(
        view_name="item-shop-stands",
        lookup_field="game_id",
        read_only=True,
    )
    shop_stands_url = serializers.HyperlinkedIdentityField(
        view_name="item-request-baskets",
        lookup_field="game_id",
        read_only=True,
    )
    colors_url = ItemColorsLinkField()
    sovereign_colors_url = SovereignColorsLinkField()

    class Meta:
        model = Item
        fields = [
            "url",
            "colors_url",
            "sovereign_colors_url",
            "game_id",
            "name",
            "string_id",
            "image_url",
            "has_colors",
            "has_metal_variants",
            "has_world_colors",
            "default_color",
            "resource_counts_url",
            "request_baskets_url",
            "next_request_basket_update",
            "shop_stands_url",
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
        ]


class URLItemResourceCountSerializer(ItemResourceCountSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name="item-resource-count-detail",
        lookup_field=["item.game_id", "world_poll.world.id"],
        lookup_url_kwarg=["item__game_id", "world_id"],
        read_only=True,
    )
    item_url = NestedHyperlinkedIdentityField(
        view_name="item-detail",
        lookup_field=["item.game_id"],
        lookup_url_kwarg=["game_id"],
        read_only=True,
    )
    world = URLSimpleWorldSerializer(source="world_poll.world")

    class Meta:
        model = ResourceCount
        fields = [
            "url",
            "item_url",
            "world",
            "is_embedded",
            "percentage",
            "count",
            "average_per_chunk",
        ]


class URLItemResourceCountTimeSeriesSerializer(ItemResourceCountSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name="item-resource-count-detail",
        lookup_field=["item.game_id", "world_poll.world.id"],
        lookup_url_kwarg=["item__game_id", "world_id"],
        read_only=True,
    )
    item_url = NestedHyperlinkedIdentityField(
        view_name="item-detail",
        lookup_field=["item.game_id"],
        lookup_url_kwarg=["game_id"],
        read_only=True,
    )

    world = URLSimpleWorldSerializer(source="world_poll.world")

    class Meta:
        model = ResourceCount
        fields = [
            "time",
            "url",
            "item_url",
            "world",
            "is_embedded",
            "percentage",
            "count",
            "average_per_chunk",
        ]


class URLSkillSerializer(SkillSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="skill-detail",
        lookup_field="id",
        read_only=True,
    )
    group = URLSimpleSkillGroupSerializer()

    class Meta:
        model = Skill
        fields = [
            "url",
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


class URLWorldShopStandPriceSerializer(WorldShopStandPriceSerializer):
    item = URLSimpleItemSerializer()

    class Meta:
        model = ItemShopStandPrice
        fields = [
            "time",
            "location",
            "item",
            "item_count",
            "price",
            "beacon_name",
            "beacon_text_name",
            "beacon_html_name",
            "guild_tag",
            "shop_activity",
        ]


class URLWorldRequestBasketPriceSerializer(WorldRequestBasketPriceSerializer):
    item = URLSimpleItemSerializer()

    class Meta:
        model = ItemRequestBasketPrice
        fields = [
            "time",
            "location",
            "item",
            "item_count",
            "price",
            "beacon_name",
            "beacon_text_name",
            "beacon_html_name",
            "guild_tag",
            "shop_activity",
        ]


class URLItemShopStandPriceSerializer(ItemShopStandPriceSerializer):
    world = URLSimpleWorldSerializer()

    class Meta:
        model = ItemShopStandPrice
        fields = [
            "time",
            "location",
            "world",
            "item_count",
            "price",
            "beacon_name",
            "beacon_text_name",
            "beacon_html_name",
            "guild_tag",
            "shop_activity",
        ]


class URLItemRequestBasketPriceSerializer(ItemRequestBasketPriceSerializer):
    world = URLSimpleWorldSerializer()

    class Meta:
        model = ItemRequestBasketPrice
        fields = [
            "time",
            "location",
            "world",
            "item_count",
            "price",
            "beacon_name",
            "beacon_text_name",
            "beacon_html_name",
            "guild_tag",
            "shop_activity",
        ]


class URLSkillGroupSerializer(SkillGroupSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="skill-group-detail",
        lookup_field="id",
        read_only=True,
    )

    class Meta:
        model = SkillGroup
        fields = [
            "url",
            "name",
            "skill_type",
            "display_name",
            "unlock_level",
        ]


class URLEmojiSerializer(EmojiSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="emoji-detail",
        lookup_field="name",
        read_only=True,
    )

    class Meta:
        model = Emoji
        fields = [
            "url",
            "names",
            "image_url",
        ]


class URLBlockSerializer(BlockSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="block-detail",
        lookup_field="game_id",
        read_only=True,
    )

    item = URLSimpleItemSerializer(source="block_item")

    class Meta:
        model = Block
        fields = [
            "url",
            "game_id",
            "name",
            "item",
        ]


class URLSimpleRecipeGroupSerializer(IDRecipeGroupSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="recipe-group-detail",
        lookup_field="id",
        read_only=True,
    )

    class Meta:
        model = RecipeGroup
        fields = [
            "url",
            "id",
            "name",
        ]


class URLRecipeGroupSerializer(RecipeGroupSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="recipe-group-detail",
        lookup_field="id",
        read_only=True,
    )
    members = URLSimpleItemSerializer(many=True)

    class Meta:
        model = RecipeGroup
        fields = [
            "url",
            "id",
            "name",
            "display_name",
            "members",
        ]


class URLRecipeRequirementSerializer(RecipeRequirementSerializer):
    skill = URLSimpleSkillSerializer()

    class Meta:
        model = RecipeRequirement
        fields = [
            "skill",
            "level",
        ]


class URLRecipeInputSerializer(RecipeInputSerializer):
    group = URLSimpleRecipeGroupSerializer(allow_null=True)
    item = URLSimpleItemSerializer(allow_null=True)

    class Meta:
        model = RecipeInput
        fields = [
            "group",
            "item",
            "count",
        ]


class URLRecipeLevelSerializer(RecipeLevelSerializer):
    inputs = URLRecipeInputSerializer(many=True)

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


class URLRecipeSerializer(RecipeSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="recipe-detail",
        lookup_field="id",
        read_only=True,
    )
    output = URLSimpleItemSerializer()
    requirements = URLRecipeRequirementSerializer(many=True)
    tints = URLSimpleItemSerializer(many=True)
    levels = URLRecipeLevelSerializer(many=True)

    class Meta:
        model = Recipe
        fields = [
            "url",
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
