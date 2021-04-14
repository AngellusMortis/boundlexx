import re
import struct
import time
from collections import namedtuple
from datetime import timedelta
from http.client import RemoteDisconnected
from io import BytesIO
from typing import Callable, Optional

from django.core.cache import cache
from django.utils.safestring import mark_safe
from PIL import Image
from requests.exceptions import ConnectionError as RequestsConnectionError

from boundlexx.boundless.client import HTTP_ERRORS

ITEM_COLOR_IDS_KEYS = "boundless:block_color_ids"
WORLD_ITEM_COLOR_IDS_KEYS = "boundless:resource_ids"
FORMATTING_REGEX = r":([^:]*):"
ERROR_THRESHOLD = 5
DEFAULT_DELAY = 5
SPHERE_GAP = 10


def convert_linear_to_s(linear):
    linear = linear / 3

    if linear <= 0.0031308:
        s = linear * 12.92
    else:
        s = 1.055 * pow(linear, 1.0 / 2.4) - 0.055

    return s


def convert_linear_rgb_to_srgb(r, g, b):
    r, g, b = (
        convert_linear_to_s(r),
        convert_linear_to_s(g),
        convert_linear_to_s(b),
    )
    return (int(r * 255), int(g * 255), int(b * 255))


def convert_linear_rgb_to_hex(r, g, b):
    r, g, b = convert_linear_rgb_to_srgb(r, g, b)

    return f"#{r:02x}{g:02x}{b:02x}"


def unpack_auth_ticket(auth_ticket):
    buffer = bytes.fromhex(auth_ticket)
    offset = 0

    gc_token_length = struct.unpack_from("<I", buffer, offset)[0]
    offset += 4

    gc_token = bytes(struct.unpack_from(f"<{gc_token_length}B", buffer, offset))
    offset += gc_token_length
    (
        session_header_length,
        unknown_1,
        unknown_2,
        ip_address_int,
        filler,
        timestamp,
        connection_count,
        ticket_length,
    ) = struct.unpack_from("<IIIIIIII", buffer, offset)
    offset += 4 * 8

    app_ownership_ticket = bytes(
        struct.unpack_from(f"<{ticket_length}B", buffer, offset)
    )

    print(
        f"""
gc_token_length: {gc_token_length}
gc_token: {gc_token.hex()}
session_header_length: {session_header_length}
unknown_1: {unknown_1}
unknown_2: {unknown_2}
ip_address_int: {ip_address_int}
filler: {filler}
timestamp: {timestamp}
connection_count: {connection_count}
ticket_length: {ticket_length}
app_ownership_ticket: {app_ownership_ticket.hex()}
"""
    )


def get_next_rank_update(ranks):
    next_update = None

    for item_rank in ranks:
        if next_update is None or item_rank.next_update < next_update:
            next_update = item_rank.next_update

    if next_update is not None:
        next_update += timedelta(minutes=5)

    return next_update


def get_block_color_item_ids():
    item_ids = cache.get(ITEM_COLOR_IDS_KEYS)

    if item_ids is None:
        from boundlexx.boundless.models import (  # noqa: E501 # pylint: disable=import-outside-toplevel,cyclic-import
            ItemColorVariant,
        )

        block_colors = (
            ItemColorVariant.objects.all().distinct("item_id").prefetch_related("item")
        )
        item_ids = [bc.item.game_id for bc in block_colors]

        cache.set(ITEM_COLOR_IDS_KEYS, item_ids, timeout=86400)

    return item_ids


def get_world_block_color_item_ids():
    item_ids = cache.get(WORLD_ITEM_COLOR_IDS_KEYS)

    if item_ids is None:
        from boundlexx.boundless.models import (  # noqa: E501 # pylint: disable=import-outside-toplevel,cyclic-import
            WorldBlockColor,
        )

        block_colors = (
            WorldBlockColor.objects.all().distinct("item_id").prefetch_related("item")
        )
        item_ids = [bc.item.game_id for bc in block_colors]

        cache.set(WORLD_ITEM_COLOR_IDS_KEYS, item_ids, timeout=86400)

    return item_ids


def color_from_hex_string(hex_string, colors=None):
    color_hex = None
    the_color = None

    try:
        int_color = int(hex_string, 16)
    except ValueError:
        pass
    else:
        if len(hex_string) in (1, 2):
            for color in colors:
                if color.game_id == int_color:
                    the_color = color
                    break
        elif len(hex_string) == 4:
            color_hex = f"#{hex_string[:3]}"
        elif len(hex_string) == 5:
            color_hex = f"#0{hex_string}"
        elif len(hex_string) >= 6:
            color_hex = f"#{hex_string[:6]}"

    return color_hex, the_color


def replace_color(string, format_string, inner, colors, strip):
    color_name = inner[1:].replace(" ", "").replace("_", "").lower()
    the_color = None
    hex_color = None
    the_color_name = None

    if color_name == "":
        color_name = "white"

    for color in colors:
        for localized in color.localizedname_set.all():
            compare_name = localized.name.replace(" ", "").replace("_", "").lower()

            if color_name == compare_name:
                the_color = color
                break

        if the_color is not None:
            break

    if the_color is None:
        hex_color, the_color = color_from_hex_string(color_name, colors=colors)

    if the_color is not None:
        hex_color = the_color.base_color
        the_color_name = (
            the_color.default_name.replace(" ", "").replace("_", "").lower()
        )

    if hex_color is not None:
        if strip:
            string = string.replace(format_string, "", 1)
        else:
            span_tag = f'<span style="color:{hex_color}" color="color">'
            if the_color_name is not None:
                span_tag = span_tag.replace('">', f' {the_color_name}">')

            string = string.replace(format_string, span_tag, 1) + "</span>"

    return string


def html_name(string, strip=False, colors=None):
    from boundlexx.boundless.models.game import (  # pylint: disable=cyclic-import
        Color,
        Emoji,
    )

    if colors is None:
        colors = list(
            Color.objects.all().prefetch_related("localizedname_set", "colorvalue_set")
        )
    final_string = string[:]

    for match in re.finditer(FORMATTING_REGEX, string):
        format_string = match.group(0)
        inner = match.group(1)

        if len(inner) == 0:
            continue

        # strip all colors
        if inner[0] == "#":
            final_string = replace_color(
                final_string, format_string, inner, colors, strip
            )
        # replace emoji with resolved emoji
        else:
            user_name = inner.lower()
            try:
                emoji = Emoji.objects.get_by_name(user_name)
            except Emoji.DoesNotExist:
                pass
            else:
                if emoji is not None:
                    if strip:
                        final_string = final_string.replace(format_string, inner, 1)
                    else:
                        html_emoji = (
                            f'<img src="{emoji.image.url}" class="emoji"'
                            f' alt="emoji {user_name}" title="{user_name}">'
                        )
                        final_string = final_string.replace(
                            format_string, html_emoji, 1
                        )

    return mark_safe(final_string)  # nosec


def calculate_extra_names(world, new_name, colors=None):
    if world.display_name != new_name:
        world.text_name = None
        world.sort_name = None
        world.html_name = None
        world.display_name = new_name

    if world.text_name is None:
        world.text_name = html_name(world.display_name, strip=True, colors=colors)

    if world.sort_name is None:
        world.sort_name = world.text_name.lower()

    if world.html_name is None:
        world.html_name = html_name(world.display_name, colors=colors)

    return world


ErrorHandlerResponse = namedtuple("ErrorHandlerResponse", ("response", "has_error"))


def crop_world(img):
    x1, y1, x2, y2 = img.getbbox()
    img = img.crop((x1 - SPHERE_GAP, y1 - SPHERE_GAP, x2 + SPHERE_GAP, y2 + SPHERE_GAP))

    return img


def clean_image(content):
    img = Image.open(BytesIO(content)).convert("RGBA")

    img = crop_world(img)

    with BytesIO() as output:
        img.save(output, format="PNG")
        content = output.getvalue()

    return content


class GameErrorHandler:
    errors: int
    delay: int
    error_threshold: int
    rd_callback: Optional[Callable]
    http_callback: Optional[Callable]
    error_callback: Optional[Callable]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        error_threshold: int = ERROR_THRESHOLD,
        delay: int = DEFAULT_DELAY,
        rd_callback: Optional[Callable] = None,
        http_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
    ):
        self.errors = 0
        self.error_threshold = error_threshold
        self.delay = delay
        self.rd_callback = rd_callback
        self.http_callback = http_callback
        self.error_callback = error_callback

    def _call_callback(self, callback, *args, **kwargs):
        if callback is not None:
            return callback(*args, **kwargs)
        return True

    def __call__(self, f):
        def error_handler(*args, **kwargs):
            response = None
            has_error = False

            try:
                response = f(*args, **kwargs)
            except HTTP_ERRORS as ex:
                has_error = True
                count = True

                if (
                    isinstance(ex, RequestsConnectionError)
                    and "RemoteDisconnected" in str(ex)
                ) or isinstance(ex, RemoteDisconnected):
                    count = self._call_callback(self.rd_callback, *args, **kwargs)
                elif (
                    hasattr(ex, "response") and ex.response is not None  # type: ignore
                ):
                    kwargs["response"] = ex.response  # type: ignore
                    count = self._call_callback(self.http_callback, *args, **kwargs)
                else:
                    kwargs["exception"] = ex
                    count = self._call_callback(self.error_callback, *args, **kwargs)

                if count:
                    self.errors += 1
                    if self.delay > 0:
                        time.sleep(self.delay)
            finally:
                if self.errors > self.error_threshold:
                    raise Exception("Aborting due to large number of HTTP errors")

            return ErrorHandlerResponse(response, has_error)

        return error_handler
