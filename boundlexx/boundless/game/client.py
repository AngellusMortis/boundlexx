from __future__ import annotations

import json
import logging
import struct
import subprocess  # nosec
import time
from collections import namedtuple
from typing import List, Optional, Union

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.functional import cached_property

from boundlexx.boundless.game.models import Settlement, ShopItem, World

logger = logging.getLogger(__name__)

QUERY_TOKEN_CACHE_KEY = "boundless_client:query_token"
QueryToken = namedtuple("QueryToken", ("player", "token", "username"))


PREFIXED_URLS = ["/worldpoll", "/gameserver/"]

MAX_TRIES_API = 500
NON_API_DECREMENT = MAX_TRIES_API // 5


class NoCharacterException(Exception):
    pass


class BoundlessClient:
    _base: str

    def __init__(self):
        self._base = settings.BOUNDLESS_API_URL_BASE

    # Offical API Endpoints

    def _get_world(self, world: World, path, api_key=False):
        delay = settings.BOUNDLESS_API_WORLD_DELAY
        if api_key:
            delay = delay * 2

        with cache.lock(f"boundless_client:lock:world:{world.id}", expire=30):
            cache_key = f"boundless_client:{world.id}"
            last_call = cache.get(cache_key) or 0
            now = time.monotonic()

            time_since = now - last_call
            if time_since < delay:
                time.sleep(delay - time_since)

            headers = {}
            if api_key and settings.BOUNDLESS_API_KEY:
                headers["Boundless-API-Key"] = settings.BOUNDLESS_API_KEY

            response = requests.get(
                f"{world.api_url}{path}",
                timeout=settings.BOUNDLESS_API_TIMEOUT,
                headers=headers,
            )
            cache.set(cache_key, time.monotonic(), timeout=10)

        return response

    def _retry_world(self, path: str, world: World, api_key: bool):
        tries = MAX_TRIES_API
        while True:
            response = self._get_world(world, path, api_key=api_key)

            try:
                response.raise_for_status()
            except requests.HTTPError as ex:
                # 403 with an API key can actually be a rate limit...
                if api_key and ex.response.status_code == 403:
                    tries -= 1
                    sleep = max(((MAX_TRIES_API + 1 - tries) // 10) % 20, 1) / 2
                    logger.info(
                        "403 error from API key at world: %s, %s Reties: %s, Sleep: %s",
                        world,
                        path,
                        tries,
                        sleep,
                    )
                    time.sleep(sleep)
                else:
                    tries -= NON_API_DECREMENT
                if tries <= 0:
                    raise
            else:
                break

        return response

    def call_world_api(
        self,
        path: str,
        world: World,
        api_key=False,
    ) -> Union[str, dict, bytes]:
        response = self._retry_world(path, world, api_key)

        response_text: Union[str, dict, bytes] = response.text
        if "Content-Type" in response.headers:
            if response.headers["Content-Type"] == "application/json":
                response_text = response.json()
            elif response.headers["Content-Type"] == "application/octet-stream":
                response_text = response.content

        return response_text

    def _shop_api(
        self,
        item_id: int,
        shop_type: str,
        world: World,
    ) -> List[ShopItem]:
        response = self.call_world_api(
            f"/shopping/{shop_type}/{item_id}", world=world, api_key=True
        )

        if not isinstance(response, bytes):
            return []

        return ShopItem.from_binary(response)

    def shop_buy(
        self,
        item_id: int,
        world: World,
    ) -> List[ShopItem]:
        return self._shop_api(item_id, "B", world=world)

    def shop_sell(
        self,
        item_id: int,
        world: World,
    ) -> List[ShopItem]:
        return self._shop_api(item_id, "S", world=world)

    # Undocumented/Private API Endpoints

    @cached_property
    def user(self):
        with cache.lock("boundless_client:lock:user", expire=10):
            cache_key = "boundless_client:last_user_index"
            user_index = cache.get(cache_key)

            user_count = len(settings.BOUNDLESS_USERNAMES)
            if user_index is None:
                user_index = 0
            cache.set(cache_key, (user_index + 1) % user_count)

        user = {"boundless": {"username": settings.BOUNDLESS_USERNAMES[user_index]}}
        if settings.BOUNDLESS_DS_REQUIRES_AUTH:
            user["boundless"]["password"] = settings.BOUNDLESS_PASSWORDS[user_index]
            user["steam"] = {
                "username": settings.STEAM_USERNAMES[user_index],
                "password": settings.STEAM_PASSWORDS[user_index],
            }

        return user

    @cached_property
    def query_token(self) -> QueryToken:
        cache_key = f"{QUERY_TOKEN_CACHE_KEY}:{self.user['boundless']['username']}"

        query_token = cache.get(cache_key)
        if query_token is not None:
            return query_token

        if settings.BOUNDLESS_DS_REQUIRES_AUTH:
            data = {
                "authToken": self._get_game_jwt(
                    self.user["boundless"]["username"],
                    self.user["boundless"]["password"],
                ),
                "steamTicket": self._get_steam_session_ticket(
                    self.user["steam"]["username"],
                    self.user["steam"]["password"],
                ),
                "vcplatform": 1,
            }
        # local sandbox server
        else:
            data = {"username": self.user["boundless"]["username"]}

        if settings.BOUNDLESS_TESTING_FEATURES:
            data.update({"gameVersion": "testing"})

        response = requests.post(
            f"{self._base}/login",
            data=json.dumps(data),
            headers={"content-type": "application/json"},
        )

        response.raise_for_status()

        data = response.json()

        if "characters" not in data:
            raise NoCharacterException("No character on this universe")

        query_token = QueryToken(
            data["characters"][0],
            data["queryToken"],
            self.user["boundless"]["username"],
        )
        cache.set(cache_key, query_token, timeout=43200)

        return query_token

    def invalidate_query_token(self):
        if "query_token" in self.__dict__:
            del self.__dict__["query_token"]

        cache.delete(f"{QUERY_TOKEN_CACHE_KEY}:{self.user['boundless']['username']}")

    def login_user(self, username, password):
        _, response = self._get_boundless_session(username, password)
        return response

    def _get_boundless_session(self, username, password):
        session = requests.Session()

        # forum email, password = forum password
        data = {
            "login": username,
            "password": password,
        }

        # Boundless Account login
        response = session.post(
            f"{settings.BOUNDLESS_ACCOUNTS_BASE_URL}/dynamic/login",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()

        return session, response.json()["user"]

    def _get_game_jwt(self, username, password):
        session, _ = self._get_boundless_session(username, password)

        # Boundless DS login
        response = session.get(
            f"{settings.BOUNDLESS_ACCOUNTS_BASE_URL}/api/v1/game-auth-token/boundless"  # noqa
        )
        response.raise_for_status()

        return response.json()["data"]

    def _get_steam_session_ticket(self, username, password):
        env = {
            # first auth will require 2FA
            # directory required to prevent future requests
            # directory can be anywhere
            "STEAM_SENTRY_DIR": settings.STEAM_SENTRY_DIR,
            "STEAM_USERNAME": username,
            "STEAM_PASSWORD": password,
            "STEAM_APP_ID": str(settings.STEAM_APP_ID),
            # node script needs this to not explode...
            "HOME": str(settings.ROOT_DIR),
            "NODE_PATH": settings.STEAM_AUTH_NODE_MODULES,
        }

        tries = 5
        while True:
            try:
                process = subprocess.run(
                    [settings.STEAM_AUTH_SCRIPT],
                    capture_output=True,
                    check=True,
                    shell=True,  # nosec
                    env=env,
                )
            except subprocess.CalledProcessError as e:
                logger.error(e.stdout)
                logger.error(e.stderr)

                if tries <= 0:
                    raise
            else:
                break

            tries -= 1
            time.sleep(5)

        return process.stdout.decode("utf8").strip()

    def _authentiated_post(
        self, path, poll_token=None, api_url=None, authenticate=True
    ):
        if poll_token:
            username = self.query_token.player["name"].lower()
            data = (
                struct.pack("<b", len(username))
                + username.encode("utf8")
                + struct.pack("<I", self.query_token.player["id"])
                + poll_token.encode("utf8")
            )
            headers = {}
        else:
            data = self.query_token.token
            for url in PREFIXED_URLS:
                if url in path:
                    data = f"q{data}"
                    break
            headers = {"Content-Type": "application/octet-stream"}

        if api_url is None:
            api_url = self._base

        response = requests.post(
            f"{api_url}{path}",
            data=data,
            timeout=settings.BOUNDLESS_API_TIMEOUT,
            headers=headers,
        )

        if response.status_code == 400 and response.text == "":
            if authenticate:
                logger.warning("Invalid auth. Renewing auth...")
                self.invalidate_query_token()
                return self._authentiated_post(
                    path,
                    poll_token=poll_token,
                    api_url=api_url,
                    authenticate=False,
                )

        return response

    def _authenticated_ds(self, path):
        with cache.lock("boundless_client:lock:ds", expire=30):
            cache_key = "boundless_client:ds"
            last_call = cache.get(cache_key) or 0
            now = time.monotonic()

            time_since = now - last_call
            if time_since < settings.BOUNDLESS_API_DS_DELAY:
                time.sleep(settings.BOUNDLESS_API_DS_DELAY - time_since)

            response = self._authentiated_post(path)
            cache.set(cache_key, time.monotonic(), timeout=10)

        return response

    def _authenticated_world(self, world: World, path, poll_token):
        username = self.user["boundless"]["password"]
        with cache.lock(
            f"boundless_client:lock:world:{world.id}:{username}", expire=30
        ):
            cache_key = f"boundless_client:{world.id}:{username}"
            last_call = cache.get(cache_key) or 0
            now = time.monotonic()

            time_since = now - last_call
            if time_since < settings.BOUNDLESS_API_WORLD_DELAY:
                time.sleep(settings.BOUNDLESS_API_WORLD_DELAY - time_since)

            response = self._authentiated_post(
                path,
                poll_token=poll_token,
                api_url=world.api_url,
                authenticate=False,
            )
            cache.set(cache_key, time.monotonic(), timeout=10)

        return response

    def get_world_data(self, world: World):
        username = self.query_token.username
        account_id = self.query_token.player["id"]

        response = self._authenticated_ds(
            f"/gameserver/{username}/{world.id}/{account_id}"
        )

        if response.status_code in (404, 410):
            return None

        response.raise_for_status()
        return response.json()

    def get_world_poll(self, world: World, poll_token=None):
        if poll_token is None:
            data = self.get_world_data(world)
            poll_token = data["pollData"]

        response = self._authenticated_world(world, "/worldpoll", poll_token)
        response.raise_for_status()

        return response.json()

    def get_world_distance(self, world_1: World, world_2: World) -> Optional[float]:
        username = self.query_token.player["name"]
        account_id = self.query_token.player["id"]

        response = self._authenticated_ds(
            f"/distance/{username}/{world_1.id}/{world_2.id}/{account_id}"
        )

        if response.status_code in (404, 410):
            return None

        response.raise_for_status()
        return response.json()["distance"]

    def get_world_settlements(self, world: World):
        response = self.call_world_api("/planet/16/5", world=world)

        if not isinstance(response, bytes):
            return []

        return Settlement.from_binary(response)
