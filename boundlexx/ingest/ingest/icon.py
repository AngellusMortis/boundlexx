# thanks to @willcrutchley, adapted from
# https://pastebin.com/u69y6X6Q
# https://pastebin.com/m4esezWe
# https://pastebin.com/79MbweER

import os
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.functional import SimpleLazyObject
from PIL import Image

from boundlexx.ingest.models import GameFile

atlas_data = SimpleLazyObject(
    lambda: GameFile.objects.get(folder="assets/gui", filename="atlas.msgpack").content
)

atlas = SimpleLazyObject(
    lambda: Image.open(
        os.path.join(settings.BOUNDLESS_LOCATION, "assets/gui/atlas.png")
    )
)


def _process_file(sprite_data):
    uvs = sprite_data["uvs"]
    # Create the output image
    size = sprite_data.get("size")
    if not size:
        size = [uvs[2], uvs[3]]
    out_img = Image.new("RGBA", (size[0], size[1]), color=(0, 0, 0, 0))

    # Image.crop(x,y,x+w,y+h) (get the sprite from atlas)
    uvs[2] = uvs[0] + uvs[2]
    uvs[3] = uvs[1] + uvs[3]
    sprite_img = atlas.crop(tuple(uvs))  # type: ignore

    # For BW images, only use the relevant colour channel
    # 0 = R, 1 = B etc...
    channel = sprite_data.get("channel")

    lower_name = sprite_data["name"].lower()
    if channel:
        sprite_img = sprite_img.getchannel(channel).convert("1", dither=0)

    # If there's no channel specified, for a BW image that means RED
    elif "emoji" in lower_name or "distance_maps_bw" in lower_name:
        sprite_img = sprite_img.getchannel(0).convert("1", dither=0)

    # Copy the sprite image into the output
    # If there's offset, use it, otherwise centre (no idea if correct)
    offset = sprite_data.get("offset")
    uvs = sprite_data["uvs"]
    sprite_img = sprite_img.crop((0, 0, uvs[2], uvs[3]))
    if offset:
        out_img.paste(
            sprite_img,
            box=(offset[0], offset[1], offset[0] + uvs[2], offset[1] + uvs[3]),
        )
    else:
        out_img.paste(sprite_img)

    # For some reason the size gets messed up again so crop back to size
    out_img = out_img.crop((0, 0, *size))

    scale = sprite_data.get("scale")
    if scale:
        factor = int(1 / scale)
        out_img = out_img.resize((size[0] * factor, size[1] * factor))

    return out_img


_cache = {}


def _get_image_from_cache(name):
    if name not in _cache:
        _cache[name] = get_image(name)

    return _cache[name]


def get_image(name):
    image = None
    for sprite_data in atlas_data["sprites"]:
        if sprite_data["name"].lower() == name.lower():
            image = _process_file(sprite_data)
            break

    return image


def get_emoji(name, layers):
    # Created later on the first layer
    out_image = None

    for i in range(1, len(layers) // 2 + 1):
        colour, layer = layers[len(layers) - 2 * i], layers[len(layers) - (2 * i) + 1]

        # Convert decimal colour to hex
        hex_colour = hex(int(colour)).split("x")[-1]
        # Convert hex colour to RGB values
        r = (int(hex_colour, 16) & 0xFF0000) >> 16
        g = (int(hex_colour, 16) & 0x00FF00) >> 8
        b = int(hex_colour, 16) & 0x0000FF

        img = _get_image_from_cache(f"emojis/{layer}")

        # If we are the first layer, create the blank canvas
        if not out_image:
            out_image = Image.new(
                "RGBA", (img.size[0], img.size[1]), color=(0, 0, 0, 0)
            )

        # Create a solid colour image from our RGB colour
        # Will be masked later by the actual emoji layer
        color_img = Image.new(
            "RGBA", (out_image.size[0], out_image.size[1]), color=(r, g, b, 255)
        )

        # Here we mask the solid colour with the parts we want to
        # appear in the final image
        out_image = Image.composite(
            color_img, out_image, img.getchannel(0).convert("1", dither=0)
        )

    return out_image


def get_django_image(image, name):
    image_content = BytesIO()
    image.save(image_content, format="PNG")

    django_image = ContentFile(image_content.getvalue())
    django_image.name = name

    return django_image
