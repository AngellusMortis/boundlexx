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
        PURGE_GROUPS,
        purge_cache,
    )

    # only purge for Boundless related models
    module_path = sender.__module__
    model_name = sender.__name__

    if (
        "boundlexx.boundless.models" in module_path
        and instance is not None
        and model_name in PURGE_GROUPS
    ):
        purge_cache.delay(model_name, instance.pk)
