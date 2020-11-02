from __future__ import annotations

import re
from typing import Dict

from django.contrib.postgres.indexes import GinIndex
from django.core.cache import cache
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from polymorphic.models import PolymorphicManager, PolymorphicModel

from boundlexx.boundless.utils import get_block_color_item_ids, get_next_rank_update
from config.storages import select_storage


class GameObjManager(PolymorphicManager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("localizedname")


class GameObj(PolymorphicModel):
    active = models.BooleanField(_("Active"), default=True)
    game_id = models.IntegerField(_("Game ID"), db_index=True)

    class Meta:
        unique_together = ("game_id", "polymorphic_ctype")
        ordering = ["game_id"]

        indexes = [
            GinIndex(fields=["game_id"]),
        ]

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
            cache.set(self.localization_cache_key, localized_name, timeout=300)
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


class LocalizedString(models.Model):
    string_id = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.string_id


class LocalizedStringText(models.Model):
    STYLE_REGEX = r"\$\[STYLE\(([^]]*),[^[]*\)\]"
    ATTRIBUTE_REGEX = r"\${(ATTRIBUTE|BUNDLE|ACTION)\(([^}]*)\)\}"
    POST_REL_REGEX = r" \(an increase of \$\{ATTRIBUTE[^}]*\}\)"

    string = models.ForeignKey(
        LocalizedString, on_delete=models.CASCADE, related_name="strings"
    )

    lang = models.CharField(_("Language"), max_length=16)
    text = models.TextField()
    _plain_text = models.TextField(blank=True, null=True)

    @property
    def plain_text(self):
        if self._plain_text is None:
            # strip styles
            self._plain_text = re.sub(
                LocalizedStringText.STYLE_REGEX, r"\g<1>", self.text
            )

            # attributes are expensive to caculate, do not do them here
            # run recalculate_plain_text for this
            matches = re.findall(LocalizedStringText.ATTRIBUTE_REGEX, self._plain_text)
            if len(matches) == 0:
                self.save()
        return self._plain_text

    class Meta:
        indexes = [
            GinIndex(fields=["text"]),
        ]


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
    color_type = models.CharField(max_length=64, choices=ColorType.choices)
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
    string_id = models.CharField(_("String ID"), max_length=64, db_index=True)
    name = models.CharField(_("Name"), max_length=64)
    mint_value = models.FloatField(_("Chrysominter Value"), null=True, blank=True)
    max_stack = models.PositiveSmallIntegerField(default=100)
    can_be_sold = models.BooleanField(db_index=True, default=True)
    list_type = models.ForeignKey(
        LocalizedString,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    description = models.ForeignKey(
        LocalizedString,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    is_resource = models.BooleanField(default=False, db_index=True)
    prestige = models.PositiveSmallIntegerField(default=0)
    mine_xp = models.PositiveSmallIntegerField(default=0)
    build_xp = models.PositiveSmallIntegerField(default=0)
    is_block = models.BooleanField(default=False, db_index=True)
    is_liquid = models.BooleanField(default=False, db_index=True)

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
    def has_colors(self):
        return self.game_id in get_block_color_item_ids()

    @property
    def next_shop_stand_update(self):
        return get_next_rank_update(self.itemsellrank_set.all())

    @property
    def next_request_basket_update(self):
        return get_next_rank_update(self.itembuyrank_set.all())


class ResourceData(models.Model):
    class Tier(models.IntegerChoices):
        TIER_1 = 0, _("T1 - Placid")
        TIER_2 = 1, _("T2 - Temperate")
        TIER_3 = 2, _("T3 - Rugged")
        TIER_4 = 3, _("T4 - Inhospitable")
        TIER_5 = 4, _("T5 - Turbulent")
        TIER_6 = 5, _("T6 - Fierce")
        TIER_7 = 6, _("T7 - Savage")
        TIER_8 = 7, _("T8 - Brutal")

    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, related_name="resource_data"
    )

    is_embedded = models.BooleanField()
    exo_only = models.BooleanField(default=False)

    max_tier = models.PositiveSmallIntegerField(
        _("Max Tier"),
        choices=Tier.choices,
        help_text=_("Max tier of world to be found on. Starts at 0."),
    )

    min_tier = models.PositiveSmallIntegerField(
        _("Min Tier"),
        choices=Tier.choices,
        help_text=_("Min tier of world to be found on. Starts at 0."),
    )

    best_max_tier = models.PositiveSmallIntegerField(
        _("Max Tier"),
        choices=Tier.choices,
        help_text=_("Max tier of world to be found on. Starts at 0."),
    )

    best_min_tier = models.PositiveSmallIntegerField(
        _("Min Tier"),
        choices=Tier.choices,
        help_text=_("Min tier of world to be found on. Starts at 0."),
    )

    shape = models.PositiveSmallIntegerField()
    size_max = models.PositiveSmallIntegerField()
    size_min = models.PositiveSmallIntegerField()
    altitude_max = models.PositiveSmallIntegerField()
    altitude_min = models.PositiveSmallIntegerField()
    distance_max = models.PositiveSmallIntegerField(blank=True, null=True)
    distance_min = models.PositiveSmallIntegerField(blank=True, null=True)
    cave_weighting = models.FloatField()
    size_skew_to_min = models.FloatField()
    blocks_above_max = models.PositiveSmallIntegerField()
    blocks_above_min = models.PositiveSmallIntegerField()
    liquid_above_max = models.PositiveSmallIntegerField()
    liquid_above_min = models.PositiveSmallIntegerField()
    noise_frequency = models.FloatField(blank=True, null=True)
    noise_threshold = models.FloatField(blank=True, null=True)
    liquid_favorite = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )
    three_d_weighting = models.FloatField()
    surface_favorite = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )
    surface_weighting = models.FloatField()
    altitude_best_lower = models.PositiveSmallIntegerField()
    altitude_best_upper = models.PositiveSmallIntegerField()
    distance_best_lower = models.PositiveSmallIntegerField(blank=True, null=True)
    distance_best_upper = models.PositiveSmallIntegerField(blank=True, null=True)
    blocks_above_best_lower = models.PositiveSmallIntegerField()
    blocks_above_best_upper = models.PositiveSmallIntegerField()
    liquid_above_best_upper = models.PositiveSmallIntegerField()
    liquid_above_best_lower = models.PositiveSmallIntegerField()
    liquid_second_favorite = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )
    surface_second_favorite = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )

    @property
    def best_world_types(self):
        types = []
        for world_type in self.best_worlds.all():
            types.append(world_type.world_type)

        return types


class ResourceDataBestWorld(models.Model):
    class WorldType(models.TextChoices):
        TYPE_LUSH = "LUSH", _("Lush")
        TYPE_METAL = "METAL", _("Metal")
        TYPE_COAL = "COAL", _("Coal")
        TYPE_CORROSIVE = "CORROSIVE", _("Corrosive")
        TYPE_SHOCK = "SHOCK", _("Shock")
        TYPE_BLAST = "BLAST", _("Blast")
        TYPE_TOXIC = "TOXIC", _("Toxic")
        TYPE_CHILL = "CHILL", _("Chill")
        TYPE_BURN = "BURN", _("Burn")
        TYPE_UMBRIS = "DARKMATTER", _("Umbris")
        TYPE_RIFT = "RIFT", _("Rift")
        TYPE_BLINK = "BLINK", _("Blink")

    data = models.ForeignKey(
        ResourceData,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="best_worlds",
    )

    world_type = models.CharField(
        _("World Type"),
        choices=WorldType.choices,
        max_length=10,
    )


class AltItem(GameObj):
    name = models.CharField(_("String ID"), max_length=64)
    base_item = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )


class Block(GameObj):
    name = models.CharField(_("Name"), max_length=64, unique=True)
    block_item = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )


class Liquid(GameObj):
    name = models.CharField(_("Name"), max_length=64, unique=True)
    block_item = models.ForeignKey(
        Item, on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )


class SkillGroup(models.Model):
    class SkillType(models.TextChoices):
        ATTRIBUTES = "Attributes", _("Attributes")
        BASIC = "Basic", _("Basic")
        EPIC = "Epic", _("Epic")

    skill_type = models.CharField(max_length=16, choices=SkillType.choices)
    name = models.CharField(max_length=16, unique=True)
    display_name = models.ForeignKey(LocalizedString, on_delete=models.CASCADE)
    unlock_level = models.PositiveIntegerField()

    class Meta:
        indexes = [
            GinIndex(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class Skill(models.Model):
    class LinkType(models.TextChoices):
        NONE = "None", _("None")
        LEFT = "Left", _("Left")
        RIGHT = "Right", _("Right")

    group = models.ForeignKey(SkillGroup, on_delete=models.CASCADE)
    number_unlocks = models.PositiveIntegerField(
        help_text=_("How many times this skill can be unlocked")
    )
    cost = models.PositiveIntegerField()
    name = models.CharField(max_length=64, unique=True)
    order = models.PositiveIntegerField()
    category = models.CharField(max_length=32)
    link_type = models.CharField(max_length=8, choices=LinkType.choices)
    description = models.ForeignKey(LocalizedString, on_delete=models.CASCADE)
    display_name = models.ForeignKey(
        LocalizedString, on_delete=models.CASCADE, related_name="+"
    )
    bundle_prefix = models.CharField(max_length=128)
    affected_by_other_skills = models.BooleanField()
    icon = models.ImageField(storage=select_storage("skills"))

    class Meta:
        indexes = [
            GinIndex(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class RecipeGroup(models.Model):
    name = models.CharField(max_length=32, unique=True)
    display_name = models.ForeignKey(LocalizedString, on_delete=models.CASCADE)
    members = models.ManyToManyField(Item)

    def __str__(self):
        return self.name


class RecipeInput(models.Model):
    group = models.ForeignKey(
        RecipeGroup, on_delete=models.CASCADE, blank=True, null=True
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    count = models.PositiveSmallIntegerField()


class RecipeLevel(models.Model):
    class Level(models.IntegerChoices):
        SINGLE = 0, _("Single")
        BULK = 1, _("Bulk")
        MASS = 2, _("Mass")

    level = models.PositiveIntegerField(choices=Level.choices)

    wear = models.PositiveIntegerField()
    spark = models.PositiveIntegerField()
    duration = models.PositiveIntegerField()
    output_quantity = models.PositiveIntegerField()
    inputs = models.ManyToManyField(RecipeInput)


class RecipeRequirement(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField()


class Recipe(GameObj):
    class MachineType(models.TextChoices):
        COMPACTOR = "COMPACTOR", _("COMPACTOR")
        CRAFTING_TABLE = "CRAFTING_TABLE", _("CRAFTING_TABLE")
        DYE_MAKER = "DYE_MAKER", _("DYE_MAKER")
        EXTRACTOR = "EXTRACTOR", _("EXTRACTOR")
        FURNACE = "FURNACE", _("FURNACE")
        MIXER = "MIXER", _("MIXER")
        REFINERY = "REFINERY", _("REFINERY")
        WORKBENCH = "WORKBENCH", _("WORKBENCH")

    class MachineLevelType(models.TextChoices):
        NONE = "", _("")
        STANDARD = "Standard", _("Standard")
        POWERED = "Powered", _("Powered")
        OVERDRIVEN = "Overdriven", _("Overdriven")
        SUPERCHARGED = "Supercharged", _("Supercharged")

    class GroupType(models.TextChoices):
        POWERED = "Powered", _("Powered")
        UNDEFINED = "Overdriven", _("Overdriven")
        SUPERCHARGED = "Supercharged", _("Supercharged")

    class EventType(models.TextChoices):
        GLEAMBOW_RACING = "GLEAMBOW_RACING", _("Gleambow Racting")
        CHRISTMAS = "CHRISTMAS", _("Christmas")
        VALENTINES = "VALENTINES", _("Valentines")
        HALLOWEEN = "HALLOWEEN", _("Halloween")
        BIRTHDAY = "BIRTHDAY", _("Birthday")

    heat = models.PositiveSmallIntegerField()
    craft_xp = models.PositiveSmallIntegerField()
    machine = models.CharField(
        max_length=16, choices=MachineType.choices, null=True, blank=True, db_index=True
    )
    output = models.ForeignKey(Item, on_delete=models.CASCADE)
    can_hand_craft = models.BooleanField()
    machine_level = models.CharField(
        max_length=16, choices=MachineLevelType.choices, null=True, blank=True
    )
    power = models.PositiveIntegerField()
    group_name = models.CharField(max_length=32)
    knowledge_unlock_level = models.PositiveIntegerField()

    tints = models.ManyToManyField(Item, related_name="+")
    requirements = models.ManyToManyField(RecipeRequirement)
    levels = models.ManyToManyField(RecipeLevel)
    required_event = models.CharField(
        max_length=16, choices=EventType.choices, null=True, blank=True
    )
    required_backer_tier = models.PositiveSmallIntegerField(null=True, blank=True)


class EmojiManager(models.Manager):
    def get_by_name(self, name):
        return (
            self.filter(active=True)
            .filter(models.Q(name=name) | models.Q(emojialtname__name=name))
            .first()
        )


class Emoji(models.Model):
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=32, db_index=True)
    image = models.ImageField(storage=select_storage("emoji"))
    is_boundless_only = models.BooleanField(default=False, db_index=True)

    objects = EmojiManager()

    def __str__(self):
        return f":{self.name}:"

    class Meta:
        indexes = [
            GinIndex(fields=["name"]),
        ]

    @cached_property
    def names(self):
        names = [self.name]

        for alt in self.emojialtname_set.all():
            names.append(alt.name)

        return names


class EmojiAltName(models.Model):
    emoji = models.ForeignKey(Emoji, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, db_index=True)

    class Meta:
        indexes = [
            GinIndex(fields=["name"]),
        ]
