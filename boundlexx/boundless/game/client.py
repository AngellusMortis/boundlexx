from typing import List, Optional

from django.utils.functional import cached_property

from boundlexx.boundless.game.models import ShopItem, World


class BoundlessClient:
    """
    BoundlessClient is intentionally left out of open source repo at the request of
    the Boundless developers. Sorry.

    This is just a stub client to make linters happy.
    """

    def shop_buy(
        self,
        item_id: int,
        world: World,
    ) -> List[ShopItem]:
        raise NotImplementedError

    def shop_sell(
        self,
        item_id: int,
        world: World,
    ) -> List[ShopItem]:
        raise NotImplementedError

    @cached_property
    def user(self):
        raise NotImplementedError

    def login_user(self, username, password):
        raise NotImplementedError

    def get_world_data(self, world: World):
        raise NotImplementedError

    def get_world_poll(self, world: World, poll_token=None):
        raise NotImplementedError

    def get_world_distance(self, world_1: World, world_2: World) -> Optional[float]:
        raise NotImplementedError

    def get_world_settlements(self, world: World):
        raise NotImplementedError
