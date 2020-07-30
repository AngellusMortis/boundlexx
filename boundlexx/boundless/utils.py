import struct
from datetime import timedelta

from CloudFlare import CloudFlare
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

CLOUDFLARE_CACHE_KEY = "boundless:cloudflare_identifier"
CLOUDFLARE_PURGE_KEY = "boundless:cloudflare_last_purge"


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

    gc_token = bytes(
        struct.unpack_from(f"<{gc_token_length}B", buffer, offset)
    )
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


def purge_cache():
    if (
        settings.CLOUDFLARE_API_TOKEN is None
        or len(settings.CLOUDFLARE_API_TOKEN) == 0
    ):
        return False

    next_purge = cache.get(CLOUDFLARE_PURGE_KEY)
    now = timezone.now()

    if next_purge is not None and now <= next_purge:
        return False

    cf = CloudFlare(token=settings.CLOUDFLARE_API_TOKEN)

    identifier = cache.get(CLOUDFLARE_CACHE_KEY)

    if identifier is None:
        r = cf.zones.get(  # pylint: disable=no-member
            params={"name": settings.CLOUDFLARE_ZONE}
        )

        identifier = r[0]["id"]
        cache.set(CLOUDFLARE_CACHE_KEY, identifier)

    cf.zones.purge_cache.post(  # pylint: disable=no-member
        identifier, data={"purge_everything": True}
    )

    next_purge = timezone.now() + timedelta(minutes=1)
    cache.set(CLOUDFLARE_PURGE_KEY, next_purge)

    return True
