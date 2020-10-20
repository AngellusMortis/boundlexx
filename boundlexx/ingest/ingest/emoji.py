import djclick as click

from boundlexx.boundless.models import Emoji, EmojiAltName
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

            image = get_emoji(name, layers)

            emoji, created = Emoji.objects.get_or_create(
                name=name,
                defaults={"image": get_django_image(image, f"{name}.png")},
            )

            alt_names = emoji_nametable.get(name)

            try:
                int(emoji.name, 16)
            except ValueError:
                emoji.is_boundless_only = True

            emoji.active = alt_names is not None
            emoji.save()

            if alt_names is not None:
                for alt_name in alt_names:
                    EmojiAltName.objects.get_or_create(emoji=emoji, name=alt_name)

            if created:
                emoji_created += 1

    print_result("emojis", emoji_created)
