import os

import djclick as click
from django.conf import settings
from django.core.files.base import ContentFile

from boundlexx.api.tasks import purge_static_cache
from boundlexx.boundless.models import (
    Color,
    ColorValue,
    Item,
    ItemColorVariant,
    LocalizedName,
    LocalizedString,
    LocalizedStringText,
    Metal,
    Subtitle,
)
from boundlexx.ingest.ingest.utils import print_result
from boundlexx.ingest.models import GameFile


def _create_generic(name, index_list, klass):
    click.echo(f"Creating {name}...")
    created = 0
    objects = {}
    with click.progressbar(index_list) as pbar:
        for index in pbar:
            obj, was_created = klass.objects.get_or_create(game_id=index)

            objects[obj.game_id] = obj

            if was_created:
                created += 1
    print_result(name, created)

    return objects


def _get_image(image_path, name):
    with open(image_path, "rb") as image_file:
        image = ContentFile(image_file.read())
        image.name = f"{name}.png"

    return image


def _create_icons(item, pbar):
    if settings.BOUNDLESS_ICONS_MAPPING.get(item.game_id):
        image_dir = os.path.join(
            settings.BOUNDLESS_ICONS_LOCATION,
            settings.BOUNDLESS_ICONS_MAPPING.get(item.game_id, ""),
        )
    else:
        image_dir = os.path.join(settings.BOUNDLESS_ICONS_LOCATION, item.name)
        if not os.path.isdir(image_dir):
            image_dir = os.path.join(settings.BOUNDLESS_ICONS_LOCATION, item.string_id)

    if os.path.isdir(image_dir):
        # default to "white" verison of item for default for colored items
        default_image = os.path.join(image_dir, "227_0.png")
        if not os.path.isfile(default_image):
            default_image = os.path.join(image_dir, "0_0.png")

        if os.path.isfile(default_image) and (
            item.image is None or not item.image.name
        ):
            item.image = _get_image(default_image, f"{item.game_id}")

    if os.path.isfile(os.path.join(image_dir, "1_0.png")):
        existing_colors = [
            i.color.game_id for i in ItemColorVariant.objects.filter(item=item)
        ]

        for color in Color.objects.exclude(game_id__in=existing_colors):
            pbar.label = f"{item.game_id}:{color.game_id}"
            pbar.render_progress()

            color_index = color.game_id - 1
            image_path = os.path.join(image_dir, f"{color_index}_{color_index}.png")
            if not os.path.isfile(image_path):
                image_path = os.path.join(image_dir, f"{color_index}_0.png")

            if os.path.isfile(image_path):
                ItemColorVariant.objects.create(
                    item=item,
                    color=color,
                    image=_get_image(
                        image_path,
                        f"{item.game_id}_{color.game_id}",
                    ),
                )


def _create_items(items_list, subtitles):
    compiled_items = GameFile.objects.get(
        folder="assets/archetypes", filename="compileditems.msgpack"
    ).content

    click.echo("Creating Items...")
    items_created = 0
    items_disabled = 0
    items = {}
    with click.progressbar(items_list, show_pos=True) as pbar:
        for item in pbar:
            string_item_id = str(item["item_id"])
            pbar.label = string_item_id
            pbar.render_progress()

            item_obj, was_created = Item.objects.get_or_create(
                game_id=item["item_id"],
                string_id=compiled_items[string_item_id]["stringID"],
            )
            item_obj.name = compiled_items[string_item_id]["name"]
            item_obj.item_subtitle = subtitles[item["subtitle_id"]]
            item_obj.mint_value = compiled_items[string_item_id]["coinValue"]
            item_obj.max_stack = compiled_items[string_item_id]["maxStackSize"]
            item_obj.can_be_sold = item_obj.game_id not in settings.BOUNDLESS_NO_SELL
            _create_icons(item_obj, pbar)

            # items that cannot be dropped or minted are not normally obtainable
            can_drop = compiled_items[string_item_id]["canDrop"]
            is_active = (
                can_drop
                and item_obj.mint_value is not None
                and item_obj.game_id not in settings.BOUNDLESS_BLACKLISTED_ITEMS
            )

            if not was_created and (not is_active and item_obj.active):
                items_disabled += 1
            item_obj.active = is_active
            item_obj.save()

            items[item_obj.game_id] = item_obj

            if was_created:
                items_created += 1

    click.echo("Purging CDN cache...")
    purge_static_cache()
    print_result("item", items_created)
    print_result("item", items_disabled, "disabled")

    return items


def _create_colors(color_list):
    color_palettes = GameFile.objects.get(
        folder="assets/archetypes", filename="compiledcolorpalettelists.msgpack"
    ).content
    colors = _create_generic("Colors", color_list, Color)

    click.echo("Creating Colors Values...")
    color_values_created = 0
    with click.progressbar(color_palettes) as pbar:
        for color_palette in pbar:
            for color_variations, color_id in color_palette["colorVariations"]:

                _, was_created = ColorValue.objects.get_or_create(
                    color=colors[color_id],
                    color_type=color_palette["name"],
                    defaults={
                        "shade": color_variations[0],
                        "base": color_variations[1],
                        "hlight": color_variations[2],
                    },
                )

                if was_created:
                    color_values_created += 1
    print_result("color values", color_values_created)

    return colors


def _create_localized_names(lang_name, lang_data, data):
    click.echo(f"Creating localized names for {lang_name}...")

    total = (
        len(lang_data["items"])
        + len(lang_data["colors"])
        + len(lang_data["metals"])
        + len(lang_data["subtitles"])
    )
    with click.progressbar(length=total) as pbar:
        localizations_created = 0
        for index, name in lang_data["colors"].items():
            l, was_created = LocalizedName.objects.get_or_create(
                game_obj=data["colors"][int(index)], lang=lang_name
            )
            l.name = name
            l.save()

            if was_created:
                localizations_created += 1

            pbar.update(1)
            pbar.render_progress()

        for index, name in lang_data["metals"].items():
            l, was_created = LocalizedName.objects.get_or_create(
                game_obj=data["metals"][int(index)], lang=lang_name
            )
            l.name = name
            l.save()

            if was_created:
                localizations_created += 1

            pbar.update(1)
            pbar.render_progress()

        for index, name in lang_data["items"].items():
            l, was_created = LocalizedName.objects.get_or_create(
                game_obj=data["items"][int(index)], lang=lang_name
            )
            l.name = name
            l.save()

            if was_created:
                localizations_created += 1

            pbar.update(1)
            pbar.render_progress()

        for index, name in lang_data["subtitles"].items():
            l, was_created = LocalizedName.objects.get_or_create(
                game_obj=data["subtitles"][int(index)], lang=lang_name
            )
            l.name = name
            l.save()

            if was_created:
                localizations_created += 1

            pbar.update(1)
            pbar.render_progress()
    print_result("localized names", localizations_created)


def _create_localization_data(strings, data):
    click.echo("Processing localization data...")
    for lang_name, lang_data in strings.items():
        _create_localized_names(lang_name, lang_data, data)

        click.echo(f"Creating localized strings for {lang_name}...")
        strings_content = GameFile.objects.get(
            folder="assets/archetypes/strings", filename=f"{lang_name}.msgpack"
        ).content

        strings_created = 0
        with click.progressbar(strings_content.items()) as pbar:
            for string_id, text in pbar:
                string, _ = LocalizedString.objects.get_or_create(string_id=string_id)

                string_text, created = LocalizedStringText.objects.get_or_create(
                    string=string, lang=lang_name, defaults={"text": text}
                )
                string_text.text = text
                string_text.save()

                if created:
                    strings_created += 1
        print_result("localized strings", strings_created)


def run():
    strings = GameFile.objects.get(
        folder="assets/archetypes", filename="itemcolorstrings.dat"
    ).content

    click.echo(
        f"""Found
{len(strings['strings']['english']['metals'])} Metals
{len(strings['strings']['english']['subtitles'])} Item Subtitles
{len(strings['items'])} Items
{len(strings['strings'])} Languages
"""
    )

    subtitles = _create_generic(
        "Subtitles", strings["strings"]["english"]["subtitles"].keys(), Subtitle
    )
    data = {
        "metals": _create_generic(
            "Metals", strings["strings"]["english"]["metals"].keys(), Metal
        ),
        "subtitles": subtitles,
        "items": _create_items(strings["items"], subtitles),
        "colors": _create_colors(strings["strings"]["english"]["colors"].keys()),
    }

    _create_localization_data(strings["strings"], data)
