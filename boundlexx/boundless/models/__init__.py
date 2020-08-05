from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from boundlexx.boundless.models.game import (
    Color,
    ColorValue,
    GameObj,
    Item,
    LocalizedName,
    Metal,
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
from boundlexx.boundless.utils import purge_cache

__all__ = [
    "GameObj",
    "LocalizedName",
    "Subtitle",
    "Color",
    "ColorValue",
    "Metal",
    "Item",
    "World",
    "WorldDistance",
    "WorldBlockColor",
    "WorldCreatureColor",
    "WorldPoll",
    "WorldPollResult",
    "ResourceCount",
    "LeaderboardRecord",
    "ItemShopStandPrice",
    "ItemRequestBasketPrice",
    "ItemBuyRank",
    "ItemSellRank",
    "ItemRank",
    "ItemShopPrice",
]


@receiver(post_save)
def check_purge_cache(sender, **kwargs):
    # only purge for Boundless related models
    if "boundlexx.boundless.models" in repr(sender):
        purge_cache()
