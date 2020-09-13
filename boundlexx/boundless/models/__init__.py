from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from boundlexx.api.utils import PURGE_GROUPS, queue_purge_paths
from boundlexx.boundless.models.game import (
    Color,
    ColorValue,
    GameObj,
    Item,
    LocalizedName,
    LocalizedString,
    LocalizedStringText,
    Metal,
    Recipe,
    RecipeGroup,
    RecipeInput,
    RecipeLevel,
    RecipeRequirement,
    Skill,
    SkillGroup,
    Subtitle,
)
from boundlexx.boundless.models.shop import (
    ItemBuyRank,
    ItemRank,
    ItemRequestBasketPrice,
    ItemSellRank,
    ItemShopPrice,
    ItemShopStandPrice,
)
from boundlexx.boundless.models.world import (
    LeaderboardRecord,
    ResourceCount,
    World,
    WorldBlockColor,
    WorldCreatureColor,
    WorldDistance,
    WorldPoll,
    WorldPollResult,
)

__all__ = [
    "Color",
    "ColorValue",
    "GameObj",
    "Item",
    "ItemBuyRank",
    "ItemRank",
    "ItemRequestBasketPrice",
    "ItemSellRank",
    "ItemShopPrice",
    "ItemShopStandPrice",
    "LeaderboardRecord",
    "LocalizedName",
    "LocalizedString",
    "LocalizedStringText",
    "Metal",
    "Recipe",
    "RecipeGroup",
    "RecipeInput",
    "RecipeLevel",
    "RecipeRequirement",
    "ResourceCount",
    "Skill",
    "SkillGroup",
    "Subtitle",
    "World",
    "WorldBlockColor",
    "WorldCreatureColor",
    "WorldDistance",
    "WorldPoll",
    "WorldPollResult",
]


@receiver(post_save, sender=World)
def queue_purge_cache_worlds(sender, instance=None, **kwargs):
    if instance is None:
        return

    paths = PURGE_GROUPS[sender.__name__]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{world_id}", str(instance.id))

    queue_purge_paths(paths)


@receiver(post_save, sender=Color)
def queue_purge_cache_colors(sender, instance=None, **kwargs):
    if instance is None:
        return

    paths = PURGE_GROUPS[sender.__name__]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{color_id}", str(instance.game_id))

    queue_purge_paths(paths)


@receiver(post_save, sender=Item)
def queue_purge_cache_items(sender, instance=None, **kwargs):
    if instance is None:
        return

    paths = PURGE_GROUPS[sender.__name__]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{item_id}", str(instance.game_id))

    queue_purge_paths(paths)


@receiver(post_save, sender=ItemShopStandPrice)
def queue_purge_cache_shop_stands(sender, instance=None, **kwargs):
    if instance is None:
        return

    paths = PURGE_GROUPS[sender.__name__]

    for index, path in enumerate(paths):
        path = path.replace("{item_id}", str(instance.item.game_id))
        paths[index] = path.replace("{world_id}", str(instance.world.id))

    queue_purge_paths(paths)


@receiver(post_save, sender=ItemRequestBasketPrice)
def queue_purge_cache_request_baskets(sender, instance=None, **kwargs):
    if instance is None:
        return

    paths = PURGE_GROUPS[sender.__name__]

    for index, path in enumerate(paths):
        path = path.replace("{item_id}", str(instance.item.game_id))
        paths[index] = path.replace("{world_id}", str(instance.world.id))

    queue_purge_paths(paths)


@receiver(post_save, sender=WorldPoll)
def queue_purge_cache_polls(sender, instance=None, **kwargs):
    if instance is None:
        return

    paths = PURGE_GROUPS[sender.__name__]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{world_id}", str(instance.world.id))

    queue_purge_paths(paths)


@receiver(post_save, sender=ResourceCount)
def queue_purge_cache_resource_counts(sender, instance=None, **kwargs):
    if instance is None:
        return

    paths = PURGE_GROUPS[sender.__name__]

    for index, path in enumerate(paths):
        paths[index] = path.replace("{item_id}", str(instance.item.game_id))

    queue_purge_paths(paths)


@receiver(post_save, sender=WorldBlockColor)
def queue_purge_cache_block_colors(sender, instance=None, **kwargs):
    if instance is None:
        return

    paths = PURGE_GROUPS[sender.__name__]

    for index, path in enumerate(paths):
        path = path.replace("{item_id}", str(instance.item.game_id))
        path = path.replace("{world_id}", str(instance.world.id))
        paths[index] = path.replace("{color_id}", str(instance.color.game_id))

    queue_purge_paths(paths)
