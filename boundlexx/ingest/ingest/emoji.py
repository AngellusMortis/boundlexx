import djclick as click

from boundlexx.boundless.models import Emoji
from boundlexx.ingest.ingest.icon import get_django_image, get_emoji
from boundlexx.ingest.ingest.utils import print_result
from boundlexx.ingest.models import GameFile


def run():
    emoji_layer_data = GameFile.objects.get(
        folder="assets/gui/emoji", filename="hash_emojis.json"
    ).content

    emoji_nametable = GameFile.objects.get(
        folder="assets/gui/emoji", filename="emoji.json"
    ).content

    emoji_created = 0
    with click.progressbar(
        range(len(emoji_layer_data) // 2), show_pos=True, show_percent=True
    ) as pbar:
        for index in pbar:
            name, layers = (
                emoji_layer_data[2 * index],
                emoji_layer_data[(2 * index) + 1],
            )

            # Nicer name from nametable (not all emojis have one)
            readable = emoji_nametable.get(name)

            # If there is a nicer name in the nametable, use this as the filename
            # Not every emoji has one though
            if readable:
                out_name = readable[0]
            else:
                out_name = name

            image = get_emoji(name, layers)

            _, created = Emoji.objects.get_or_create(
                name=out_name,
                defaults={"image": get_django_image(image, f"emoji/{out_name}.png")},
            )

            if created:
                emoji_created += 1

    print_result("emojis", emoji_created)
