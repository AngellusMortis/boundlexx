import re
import struct
from datetime import timedelta

from django.core.cache import cache
from django.utils.safestring import mark_safe

ITEM_COLOR_IDS_KEYS = "boundless:resource_ids"
FORMATTING_REGEX = r":([^:]*):"


def convert_linear_to_s(linear):
    if linear <= 0.0031308:
        s = linear * 12.92
    s = 1.055 * pow(linear, 1.0 / 2.4) - 0.055

    # clamp value to 8-bit space
    if s < 0.0:
        s = 0.0
    elif s > 1.0:
        s = 1.0
    return s


def convert_linear_rgb_to_hex(r, g, b):
    r, g, b = (
        convert_linear_to_s(r),
        convert_linear_to_s(g),
        convert_linear_to_s(b),
    )
    r, g, b = int(r * 255), int(g * 255), int(b * 255)

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
            WorldBlockColor,
        )

        block_colors = (
            WorldBlockColor.objects.all().distinct("item_id").prefetch_related("item")
        )
        item_ids = [bc.item.game_id for bc in block_colors]

        cache.set(ITEM_COLOR_IDS_KEYS, item_ids, timeout=86400)

    return item_ids


def strip_formatting(string):
    final_string = string[:]
    for match in re.finditer(FORMATTING_REGEX, string):
        format_string = match.group(0)
        inner = match.group(1)

        # strip all colors
        if inner[0] == "#":
            final_string = final_string.replace(format_string, "", 1)
        # replace emoji with their emoji name
        else:
            final_string = final_string.replace(format_string, inner, 1)

    return final_string


def replace_color(string, format_string, inner, colors):
    color_name = inner[1:].replace(" ", "").replace("_", "").lower()
    the_color = None
    hex_color = None
    the_color_name = None

    for color in colors:
        for localized in color.localizedname_set.all():
            compare_name = localized.name.replace(" ", "").replace("_", "").lower()

            if color_name == compare_name:
                the_color = color
                break

        if the_color is not None:
            break

    if the_color is not None:
        hex_color = the_color.base_color
        the_color_name = (
            the_color.default_name.replace(" ", "").replace("_", "").lower()
        )
    else:
        try:
            int(color_name, 16)
        except ValueError:
            pass
        else:
            hex_color = inner

    if hex_color is not None:
        span_tag = f'<span style="color:{hex_color}" color="color">'
        if the_color_name is not None:
            span_tag = span_tag.replace('">', f' {the_color_name}">')

        string = string.replace(format_string, span_tag, 1) + "</span>"
    else:
        string = string.replace(format_string, "", 1)

    return string


def html_name(string, colors=None):
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

        # strip all colors
        if inner[0] == "#":
            final_string = replace_color(final_string, format_string, inner, colors)
        # replace emoji with resolved emoji
        else:
            try:
                emoji = Emoji.objects.get_by_name(inner.lower())
            except Emoji.DoesNotExist:
                pass
            else:
                html_emoji = f'<img src="{emoji.image.url}" class="emoji">'
                final_string = final_string.replace(format_string, html_emoji, 1)

    return mark_safe(final_string)  # nosec


def calculate_extra_names(world, new_name, colors=None):
    if world.display_name != new_name:
        world.text_name = None
        world.sort_name = None
        world.html_name = None

    if world.text_name is None:
        world.text_name = strip_formatting(world.display_name)

    if world.sort_name is None:
        world.sort_name = world.text_name.lower()

    if world.html_name is None:
        world.html_name = html_name(world.display_name, colors=colors)

    world.display_name = new_name

    return world
