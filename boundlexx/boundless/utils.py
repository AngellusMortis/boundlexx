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
