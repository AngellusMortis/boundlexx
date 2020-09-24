import json

import djclick as click
from bs4 import BeautifulSoup

from boundlexx.boundless.models import Color, ForumImage


@click.command()
@click.argument("json_file", type=click.File("r"))
def command(json_file):
    forum_colors = json.load(json_file)

    colors = list(Color.objects.all().order_by("game_id"))
    color_images = {}

    for key, value in forum_colors["short"].items():
        color_images[int(key)] = {"shortcut_url": value}

    raw_html = BeautifulSoup(forum_colors["long"], "html.parser")
    images = raw_html.find_all("img")

    for image in images:
        color_id = int(image.get("alt").split(" ")[-1])

        color_images[color_id]["checksum"] = image.get("data-base62-sha1")
        color_images[color_id]["url"] = image.get("src")

    num_created = 0
    for color_id, data in color_images.items():
        if color_id == 0:
            continue
        _, created = ForumImage.objects.get_or_create(
            game_obj=colors[color_id - 1], **data
        )

        if created:
            num_created += 1

    click.echo(f"Created {num_created} ForumImage(s)")
