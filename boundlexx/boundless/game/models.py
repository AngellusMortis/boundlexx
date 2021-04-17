from __future__ import annotations

import socket
import zlib
from collections import namedtuple
from dataclasses import dataclass
from http.client import RemoteDisconnected
from struct import unpack_from
from typing import List, Union

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import RequestException
from urllib3.exceptions import (
    HTTPError,
    MaxRetryError,
    NewConnectionError,
    ProtocolError,
)

HTTP_ERRORS = (
    ConnectionError,
    HTTPError,
    MaxRetryError,
    NewConnectionError,
    ProtocolError,
    RemoteDisconnected,
    RequestException,
    RequestsConnectionError,
    socket.error,
    socket.gaierror,
    socket.timeout,
)

World = namedtuple("World", ("id", "api_url"))


@dataclass
class Location:
    x: int
    y: Union[int, None]
    z: int

    def __str__(self):
        if self.y is not None:
            return f"({self.x}, {self.z}) Alt: {self.y}"
        return f"({self.x}, {self.z})"


@dataclass
class ShopItem:
    beacon_name: str
    guild_tag: str
    item_count: int
    shop_activity: int
    price: int
    location: Location

    @staticmethod
    def from_binary(binary: bytes) -> List[ShopItem]:
        items = []

        offset = 0
        while offset != len(binary):
            # Read more below:
            # https://docs.playboundless.com/modding/http-shopping.html

            beacon_name_length, guild_tag_length = unpack_from("<BB", binary, offset)
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


@dataclass
class Settlement:
    name: str
    prestige: int
    location: Location

    @staticmethod
    def from_binary(binary: bytes) -> List[Settlement]:
        binary = zlib.decompress(binary[5:])

        offset = 8

        count = unpack_from("<I", binary, offset)[0]
        offset += 4

        settlements: List[Settlement] = []

        while len(settlements) < count and offset < len(binary):
            name_length = unpack_from("<B", binary, offset)[0]
            offset += 1

            name, prestige, _, x, z = unpack_from(
                f"<{name_length}sIIhh", binary, offset
            )
            offset += name_length + 12

            settlements.append(
                Settlement(
                    name.decode("latin1"), prestige, Location(x * 16, None, -z * 16)
                )
            )

        return settlements
