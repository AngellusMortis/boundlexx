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
def check_purge_cache(sender, instance=None, **kwargs):
    from boundlexx.api.tasks import (  # pylint: disable=cyclic-import
        purge_cache,
    )

    # only purge for Boundless related models
    module_path = sender.__module__
    if "boundlexx.boundless.models" in module_path and instance is not None:
        purge_cache.delay(sender.__name__, instance.pk)
