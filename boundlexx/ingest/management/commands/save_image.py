import os

import djclick as click
from django.conf import settings

from boundlexx.ingest.ingest.icon import (
    atlas_data,
    emoji_layer_data,
    get_emoji,
    get_image,
)


def _save_image_file(name, image, do_print=False):
    if image is None:
        if do_print:
            click.echo(f"No image data for {name}")
        return

    file_path = os.path.join(settings.ROOT_DIR, "icons", name)
    dir_path = os.path.dirname(file_path)

    os.makedirs(dir_path, exist_ok=True)

    if do_print:
        click.echo(f"Saving {name}...")
    try:
        image.save(file_path)
    except ValueError:
        if do_print:
            click.echo(f"Failed to save {name}")


def _save_image(name, sprite_data=None):
    image = get_image(name, sprite_data=sprite_data)

    _save_image_file(name, image, sprite_data is None)


def _save_emoji(name, layers=None):
    image = get_emoji(name, layers=layers)

    name = os.path.join("emojis", f"{name}.png")

    _save_image_file(name, image, layers is None)


@click.command()
@click.option(
    "--emojis",
    is_flag=True,
)
@click.option(
    "--images",
    is_flag=True,
)
@click.option("-n", "--name", required=False)
@click.option("-e", "--emoji", required=False)
def command(name=None, emoji=None, emojis=False, images=False, **kwargs):
    if name is not None:
        _save_image(name)
        return

    if emoji is not None:
        _save_emoji(emoji)
        return

    if not images and not emojis:
        images = True
        emojis = True

    if images:
        click.echo("Saving images...")
        with click.progressbar(
            atlas_data["sprites"], show_pos=True, show_percent=True
        ) as pbar:
            for sprite_data in pbar:
                _save_image(sprite_data["name"].lower(), sprite_data=sprite_data)

    if emojis:
        click.echo("Saving emojis...")
        with click.progressbar(
            range(len(emoji_layer_data) // 2), show_pos=True, show_percent=True
        ) as pbar:
            for index in pbar:
                name, layers = (
                    emoji_layer_data[2 * index],
                    emoji_layer_data[(2 * index) + 1],
                )

                _save_emoji(name, layers)
