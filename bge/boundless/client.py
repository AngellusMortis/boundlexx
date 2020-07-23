from __future__ import annotations

import time
from dataclasses import dataclass
from struct import unpack_from
from typing import Dict, List, Optional, Union

import requests
from django.conf import settings
from django.core.cache import cache


@dataclass
class Location:
    x: int
    y: int
    z: int

    def __str__(self):
        return f"({self.x}, {self.z}) Alt: {self.y}"


@dataclass
class ShopItem:
    beacon_name: str
    guild_tag: str
    item_count: int
    shop_activity: int
    price: int
    location: Location

    @staticmethod
    def from_binary(binary) -> List[ShopItem]:
        items = []

        offset = 0
        while offset != len(binary):
            # Read more below:
            # https://forum.playboundless.com/t/http-shopping-api-documentation/41598
            # https://gist.github.com/jamesaustin/2be04dc868cca9d5b5fea1f6e9dfc67c

            beacon_name_length, guild_tag_length = unpack_from(
                "<BB", binary, offset
            )
            (
                beacon_name,
                guild_tag,
                item_count,
                shop_activity,
                price,
                location_x,
                location_z,
                location_y,
            ) = unpack_from(
                f"<{beacon_name_length}s{guild_tag_length}sIIqhhB",
                binary,
                offset + 2,
            )
            offset += 23 + beacon_name_length + guild_tag_length

            beacon_name = beacon_name.decode("latin1")
            guild_tag = guild_tag.decode("latin1")

            location = Location(location_x, location_y, -location_z)
            items.append(
                ShopItem(
                    beacon_name,
                    guild_tag,
                    item_count,
                    shop_activity,
                    price / 100,
                    location,
                )
            )

        return items


class BoundlessClient:
    def api_url(self, path: str):
        return f"{settings.BOUNDLESS_API_URL_BASE}{path}"

    def world_url(self, world, path):
        if world not in self.gameservers.keys():
            raise ValueError("invalid world")

        return f"{self.gameservers[world]['apiURL']}{path}"

    @property
    def gameservers(self) -> dict:
        cache_key = "boundless:gameservers"
        servers = cache.get(cache_key)

        if servers is None:
            response = requests.get(
                self.api_url("/list-gameservers"),
                timeout=settings.BOUNDLESS_API_TIMEOUT,
            )

            response.raise_for_status()
            servers = {}
            for server in response.json():
                servers[server["name"]] = server

            cache.set(cache_key, servers, 300)

        return servers

    def _get_world(self, world, path):
        with cache.lock("boundless_client:lock", expire=10):
            cache_key = f"boundless_client:{world}"
            last_call = cache.get(cache_key) or 0
            now = time.monotonic()

            time_since = now - last_call
            if time_since < settings.BOUNDLESS_API_WORLD_DELAY:
                time.sleep(settings.BOUNDLESS_API_WORLD_DELAY - time_since)

            response = requests.get(
                self.world_url(world, path),
                timeout=settings.BOUNDLESS_API_TIMEOUT,
            )
            cache.set(cache_key, time.monotonic())

        return response

    def call_world_api(
        self, path: str, worlds: Optional[List[str]] = None
    ) -> Dict[str, Union[str, dict, bytes]]:
        all_worlds = list(self.gameservers.keys())
        if worlds is None:
            worlds = list(self.gameservers.keys())

        responses: Dict[str, Union[str, dict, bytes]] = {}
        for world in worlds:
            if world not in all_worlds:
                raise ValueError("invalid world")

            tries = 5
            while True:
                response = self._get_world(world, path)

                try:
                    response.raise_for_status()
                except requests.HTTPError:
                    tries -= 1
                    if tries == 0:
                        raise
                else:
                    break

            response_text: Union[str, dict, bytes] = response.text
            if "Content-Type" in response.headers:
                if response.headers["Content-Type"] == "application/json":
                    response_text = response.json()
                elif (
                    response.headers["Content-Type"]
                    == "application/octet-stream"
                ):
                    response_text = response.content

            responses[world] = response_text

        return responses

    def _shop_api(
        self, item_id: int, shop_type: str, worlds: Optional[List[str]] = None
    ) -> Dict[str, List[ShopItem]]:
        response = self.call_world_api(
            f"/shopping/{shop_type}/{item_id}", worlds=worlds
        )

        items = {}
        for world, binary in response.items():
            items[world] = ShopItem.from_binary(binary)

        return items

    def shop_buy(
        self, item_id: int, worlds: Optional[List[str]] = None
    ) -> Dict[str, List[ShopItem]]:
        return self._shop_api(item_id, "B", worlds=worlds)

    def shop_sell(
        self, item_id: int, worlds: Optional[List[str]] = None
    ) -> Dict[str, List[ShopItem]]:
        return self._shop_api(item_id, "S", worlds=worlds)
