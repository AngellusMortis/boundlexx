from django.utils.translation import ugettext as _
from rest_framework import serializers

from boundlexx.api.serializers.base import (
    AzureImageField,
    ItemColorsLinkField,
    LocalizedNameSerializer,
    LocalizedStringSerializer,
    LocationSerializer,
    NestedHyperlinkedIdentityField,
    ResourceCountLinkField,
    SimpleItemSerializer,
    SimpleSkillGroupSerializer,
    SimpleWorldSerializer,
    SovereignColorsLinkField,
)
from boundlexx.boundless.models import (
    Block,
    Color,
    Emoji,
    Item,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    ResourceCount,
    Skill,
    SkillGroup,
    Subtitle,
)
from boundlexx.ingest.models import GameFile


class ColorSerializer(serializers.ModelSerializer):
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
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
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
        ]


class SubtitleSerializer(serializers.ModelSerializer):
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )

    class Meta:
        model = Subtitle
        fields = ["localization"]


class ItemSerializer(serializers.ModelSerializer):
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
    localization = LocalizedNameSerializer(
        source="localizedname_set",
        many=True,
    )
    item_subtitle = SubtitleSerializer()

    next_shop_stand_update = serializers.DateTimeField(allow_null=True)
    next_request_basket_update = serializers.DateTimeField(allow_null=True)

    list_type = LocalizedStringSerializer()
    description = LocalizedStringSerializer()

    class Meta:
        model = Item
        fields = [
            "url",
            "colors_url",
            "sovereign_colors_url",
            "game_id",
            "name",
            "string_id",
            "resource_counts_url",
            "request_baskets_url",
            "next_request_basket_update",
            "shop_stands_url",
            "next_shop_stand_update",
            "localization",
            "item_subtitle",
            "mint_value",
            "list_type",
            "description",
        ]


class ItemResourceCountSerializer(serializers.ModelSerializer):
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
    world = SimpleWorldSerializer(source="world_poll.world")

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


class ItemResourceCountTimeSeriesSerializer(ItemResourceCountSerializer):
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


class SkillSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="skill-detail",
        lookup_field="id",
        read_only=True,
    )
    group = SimpleSkillGroupSerializer()
    display_name = LocalizedStringSerializer()
    description = LocalizedStringSerializer()
    icon_url = AzureImageField(source="icon", allow_null=True)

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


class SimpleWorldShopPriceSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()
    location = LocationSerializer()


class SimpleWorldShopStandPriceSerializer(SimpleWorldShopPriceSerializer):
    class Meta:
        model = ItemShopStandPrice
        fields = [
            "time",
            "location",
            "item",
            "item_count",
            "price",
            "beacon_name",
            "guild_tag",
            "shop_activity",
        ]


class SimpleWorldRequestBasketPriceSerializer(SimpleWorldShopPriceSerializer):
    class Meta:
        model = ItemRequestBasketPrice
        fields = [
            "time",
            "location",
            "item",
            "item_count",
            "price",
            "beacon_name",
            "guild_tag",
            "shop_activity",
        ]


class SimpleItemShopPriceSerializer(serializers.ModelSerializer):
    world = SimpleWorldSerializer()
    location = LocationSerializer()


class SimpleItemShopStandPriceSerializer(SimpleItemShopPriceSerializer):
    class Meta:
        model = ItemShopStandPrice
        fields = [
            "time",
            "location",
            "world",
            "item_count",
            "price",
            "beacon_name",
            "guild_tag",
            "shop_activity",
        ]


class SimpleItemRequestBasketPriceSerializer(SimpleItemShopPriceSerializer):
    class Meta:
        model = ItemRequestBasketPrice
        fields = [
            "time",
            "location",
            "world",
            "item_count",
            "price",
            "beacon_name",
            "guild_tag",
            "shop_activity",
        ]


class SkillGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="skill-group-detail",
        lookup_field="id",
        read_only=True,
    )
    display_name = LocalizedStringSerializer()

    class Meta:
        model = SkillGroup
        fields = [
            "url",
            "name",
            "skill_type",
            "display_name",
            "unlock_level",
        ]


class SimpleGameFileSerializer(serializers.ModelSerializer):
    file_type = serializers.ChoiceField(
        source="get_file_type_display",
        help_text=_("0 = JSON, 1 = MSGPACK, 2 = OTHER"),
        choices=GameFile.Filetype.choices,
    )
    url = serializers.HyperlinkedIdentityField(
        view_name="game-file-detail",
        lookup_field="id",
        read_only=True,
    )

    class Meta:
        model = GameFile
        fields = [
            "url",
            "folder",
            "filename",
            "file_type",
            "game_version",
        ]


class GameFileSerializer(SimpleGameFileSerializer):
    class Meta:
        model = GameFile
        fields = [
            "url",
            "folder",
            "filename",
            "file_type",
            "game_version",
            "content",
        ]


class EmojiSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="emoji-detail",
        lookup_field="name",
        read_only=True,
    )
    image_url = AzureImageField(source="image", allow_null=True)

    class Meta:
        model = Emoji
        fields = [
            "url",
            "names",
            "image_url",
        ]


class BlockSerialzier(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="block-detail",
        lookup_field="game_id",
        read_only=True,
    )

    item = SimpleItemSerializer(source="block_item")

    class Meta:
        model = Block
        fields = [
            "url",
            "game_id",
            "name",
            "item",
        ]
