import struct


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
