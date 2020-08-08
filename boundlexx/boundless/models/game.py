from __future__ import annotations

from typing import Dict

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.core.cache import cache
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from polymorphic.models import PolymorphicManager, PolymorphicModel


class GameObjManager(PolymorphicManager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("localizedname")


class GameObj(PolymorphicModel):
    active = models.BooleanField(_("Active"), default=True)
    game_id = models.IntegerField(_("Game ID"), db_index=True)

    class Meta:
        unique_together = ("game_id", "polymorphic_ctype")
        ordering = ["game_id"]

    def __str__(self):
        if self.default_name:
            return f"{self.game_id}: {self.default_name}"
        return str(self.game_id)

    @cached_property
    def localized_names(self):
        names = {}
        for name in self.localizedname_set.all():
            names[name.lang] = name.name
        return names

    @cached_property
    def localization_cache_key(self):
        return f"localized_name:{self.polymorphic_ctype_id}_{self.game_id}"

    @cached_property
    def default_name(self):
        localized_name = cache.get(self.localization_cache_key)

        if localized_name is None:
            localized_name = self.localized_names.get("english")
            cache.set(self.localization_cache_key, localized_name)
        return localized_name


class LocalizedName(
    ExportModelOperationsMixin("localized_name"), PolymorphicModel  # type: ignore  # noqa E501
):
    game_obj = models.ForeignKey(GameObj, on_delete=models.CASCADE)
    lang = models.CharField(_("Language"), max_length=16)
    name = models.CharField(_("Name"), max_length=128, db_index=True)

    class Meta:
        unique_together = ("game_obj", "lang")
        indexes = [
            GinIndex(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.lang}: {self.name}"


class Subtitle(ExportModelOperationsMixin("subtitle"), GameObj):  # type: ignore # noqa E501
    pass


class Color(ExportModelOperationsMixin("color"), GameObj):  # type: ignore
    @cached_property
    def base_color(self):
        colors: Dict[int, int] = {}

        for color in self.colorvalue_set.all():
            color_count = colors.get(color.base, 0) + 1

            colors[color.base] = color_count

        base_color = None
        highest_count = -1
        for color_value, count in colors.items():
            if count > highest_count:
                highest_count = count
                base_color = color_value

        if base_color is None:
            return None

        return f"#{base_color:06x}"

    @cached_property
    def gleam_color(self):
        for color in self.colorvalue_set.all():
            if color.color_type == ColorValue.ColorType.GLEAM:
                return color.rgb_color
        return None


class ColorValue(ExportModelOperationsMixin("color_value"), models.Model):  # type: ignore # noqa E501
    class ColorType(models.TextChoices):
        CHARACTER = "CHARACTER", _("CHARACTER")
        CHARACTER_DECAL = "CHARACTER_DECAL", _("CHARACTER_DECAL")
        CREATURE_BASE = "CREATURE_BASE", _("CREATURE_BASE")
        CREATURE_AUX = "CREATURE_AUX", _("CREATURE_AUX")
        CREATURE_EXOTIC = "CREATURE_EXOTIC", _("CREATURE_EXOTIC")
        WOOD = "WOOD", _("WOOD")
        ROCK = "ROCK", _("ROCK")
        GRASS = "GRASS", _("GRASS")
        ICE = "ICE", _("ICE")
        GLACIER = "GLACIER", _("GLACIER")
        SOIL = "SOIL", _("SOIL")
        ASH = "ASH", _("ASH")
        GLEAM = "GLEAM", _("GLEAM")
        GRAVEL = "GRAVEL", _("GRAVEL")
        GROWTH = "GROWTH", _("GROWTH")
        MOULD = "MOULD", _("MOULD")
        SAND = "SAND", _("SAND")
        SPONGE = "SPONGE", _("SPONGE")
        LEAVES = "LEAVES", _("LEAVES")
        MANTLE = "MANTLE", _("MANTLE")
        MUD = "MUD", _("MUD")
        TANGLE = "TANGLE", _("TANGLE")
        THORNS = "THORNS", _("THORNS")
        FLORA_1 = "FLORA_1", _("FLORA_1")
        FLORA_DECAL_1 = "FLORA_DECAL_1", _("FLORA_DECAL_1")
        FLORA_2 = "FLORA_2", _("FLORA_2")
        FLORA_DECAL_2 = "FLORA_DECAL_2", _("FLORA_DECAL_2")
        FLORA_3 = "FLORA_3", _("FLORA_3")
        FLORA_DECAL_3 = "FLORA_DECAL_3", _("FLORA_DECAL_3")
        FLORA_4 = "FLORA_4", _("FLORA_4")
        FLORA_DECAL_4 = "FLORA_DECAL_4", _("FLORA_DECAL_4")
        INK = "INK", _("INK")
        FIBER = "FIBER", _("FIBER")

    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    color_type = models.CharField(max_length=16, choices=ColorType.choices)
    shade = models.IntegerField()
    base = models.IntegerField()
    hlight = models.IntegerField()

    class Meta:
        unique_together = ("color", "color_type")

    @property
    def rgb_color(self):
        if self.base is None:
            return None
        return f"#{self.base:06x}"


class Metal(ExportModelOperationsMixin("metal"), GameObj):  # type: ignore
    pass


class Item(ExportModelOperationsMixin("item"), GameObj):  # type: ignore
    item_subtitle = models.ForeignKey(
        Subtitle, on_delete=models.SET_NULL, blank=True, null=True
    )
    string_id = models.CharField(_("String ID"), max_length=64)

    class Meta:
        indexes = [
            GinIndex(fields=["string_id"]),
        ]

    @property
    def default_name(self):  # pylint: disable=invalid-overridden-method
        return self.string_id

    @property
    def english(self):
        return super().default_name

    @property
    def buy_locations(self):
        return self.itemshopstandprice_set.filter(active=True)

    @property
    def sell_locations(self):
        return self.itemrequestbasketprice_set.filter(active=True)

    @property
    def is_resource(self):
        return self.game_id in settings.BOUNDLESS_WORLD_POLL_RESOURCE_MAPPING

    @property
    def has_colors(self):
        return self.worldblockcolor_set.count() > 0
