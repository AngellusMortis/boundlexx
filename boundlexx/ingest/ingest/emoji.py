import djclick as click
import requests
from django.conf import settings

from boundlexx.boundless.models import Emoji, EmojiAltName
from boundlexx.ingest.ingest.icon import get_django_image, get_emoji
from boundlexx.ingest.ingest.utils import print_result
from boundlexx.ingest.models import GameFile

GROUP_TO_CATEGORY = {
    "smileys-emotion": "SMILEY",
    "people-body": "PEOPLE",
    "component": "COMPONENT",
    "animals-nature": "ANIMAL",
    "food-drink": "FOOD",
    "travel-places": "TRAVEL",
    "activities": "ACTIVITIES",
    "objects": "OBJECTS",
    "symbols": "SYMBOLS",
    "flags": "FLAGS",
}


def _get_emoji_list():
    if settings.EMOJI_API_KEY is None:
        click.echo("WARNING: EMOJI_API_KEY missing")
        return []

    click.echo("Getting emoji category list...")
    response = requests.get(
        f"https://emoji-api.com/emojis?&access_key={settings.EMOJI_API_KEY}"
    )
    response.raise_for_status()

    return response.json()


def run():
    emoji_list = _get_emoji_list()

    emoji_layer_data = GameFile.objects.get(
        folder="assets/gui/emoji", filename="hash_emojis.json"
    ).content

    emoji_nametable = GameFile.objects.get(
        folder="assets/gui/emoji", filename="emoji.json"
    ).content

    emoji_created = 0
    click.echo("Importing emojis...")
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
                emoji.category = "BOUNDLESS"
            else:
                lookup = emoji.name.upper()

                for emoji_dict in emoji_list:
                    if lookup in emoji_dict["codePoint"].split(" "):
                        emoji.category = GROUP_TO_CATEGORY[emoji_dict["group"]]

            if emoji.category is None:
                emoji.category = Emoji.EmojiCategory.UNCATEGORIZED

            emoji.active = alt_names is not None
            emoji.save()

            if alt_names is not None:
                for alt_name in alt_names:
                    EmojiAltName.objects.get_or_create(emoji=emoji, name=alt_name)

            if created:
                emoji_created += 1

    print_result("emojis", emoji_created)
