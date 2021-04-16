from rest_framework import serializers
from rest_framework.relations import Hyperlink
from rest_framework.reverse import reverse

from boundlexx.api.common.serializers import SimpleItemSerializer
from boundlexx.boundless.models import Item, SkillGroup, World


class NestedHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def get_url(
        self,
        obj,
        view_name,
        request,
        format,  # pylint: disable=redefined-builtin # noqa A002
    ):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None

        kwargs = {}
        for index, lookup_field in enumerate(self.lookup_field):
            attrs = lookup_field.split(".")

            lookup_value = obj
            for attr in attrs:
                lookup_value = getattr(lookup_value, attr)

            kwargs[self.lookup_url_kwarg[index]] = lookup_value

        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


class ActiveWorldUrlHyperlinkField(serializers.HyperlinkedIdentityField):
    def get_url(
        self,
        obj,
        view_name,
        request,
        format,  # pylint: disable=redefined-builtin  # noqa A002
    ):
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None

        if not obj.active:
            return None

        return super().get_url(obj, view_name, request, format)


class ResourceCountLinkField(serializers.ModelField):
    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["model_field"] = None
        kwargs["allow_null"] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):  # pylint: disable=arguments-differ
        return Hyperlink(value, None)

    def get_attribute(self, obj):
        if obj.is_resource:
            return reverse(
                "item-resource-count-list",
                kwargs={"item__game_id": obj.game_id},
                request=self.context["request"],
            )
        return None


class SovereignColorsLinkField(serializers.ModelField):
    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["model_field"] = None
        kwargs["allow_null"] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):  # pylint: disable=arguments-differ
        return Hyperlink(value, None)

    def get_attribute(self, obj):
        if obj.has_world_colors:
            return reverse(
                "item-sovereign-colors",
                kwargs={"game_id": obj.game_id},
                request=self.context["request"],
            )
        return None


class ShopURL(serializers.ModelField):
    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["model_field"] = None
        kwargs["allow_null"] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):  # pylint: disable=arguments-differ
        return Hyperlink(value, None)

    def get_url(self, obj):
        return None

    def get_attribute(self, obj):
        if not obj.is_creative:
            return self.get_url(obj)
        return None


class RequestBasketsURL(ShopURL):
    def get_url(self, obj):
        if not obj.is_public or obj.is_creative:
            return None

        return reverse(
            "world-request-baskets",
            kwargs={"id": obj.id},
            request=self.context["request"],
        )


class ShopStandsURL(ShopURL):
    def get_url(self, obj):
        if not obj.is_public or obj.is_creative:
            return None

        return reverse(
            "world-shop-stands",
            args={"id": obj.id},
            request=self.context["request"],
        )


class ItemColorsLinkField(serializers.ModelField):
    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        kwargs["model_field"] = None
        kwargs["allow_null"] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):  # pylint: disable=arguments-differ
        return Hyperlink(value, None)

    def get_attribute(self, obj):
        if obj.has_world_colors:
            return reverse(
                "item-colors-list",
                kwargs={"item__game_id": obj.game_id},
                request=self.context["request"],
            )
        return None


class URLSimpleWorldSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="world-detail",
        lookup_field="id",
        read_only=True,
    )
    id = serializers.IntegerField()  # noqa: A003

    class Meta:
        model = World
        fields = [
            "url",
            "id",
            "active",
            "display_name",
            "text_name",
            "html_name",
        ]


class URLSimpleSkillGroupSerializer(serializers.ModelSerializer):
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
        ]


class URLSimpleSkillSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="skill-detail",
        lookup_field="id",
        read_only=True,
    )

    class Meta:
        model = SkillGroup
        fields = [
            "url",
            "name",
        ]


class URLSimpleItemSerializer(SimpleItemSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="item-detail",
        lookup_field="game_id",
        read_only=True,
    )

    class Meta:
        model = Item
        fields = [
            "url",
            "game_id",
            "name",
            "string_id",
            "image_url",
            "has_colors",
            "has_metal_variants",
            "has_world_colors",
            "default_color",
            "is_resource",
        ]


class SimpleColorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="color-detail",
        lookup_field="game_id",
        read_only=True,
    )

    class Meta:
        model = Item
        fields = [
            "url",
            "game_id",
        ]
