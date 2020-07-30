from collections import namedtuple
from struct import unpack_from
from typing import Dict, List

import djclick as click
import msgpack
from django.conf import settings

from boundlexx.boundless.models import (
    Color,
    Item,
    LocalizedName,
    Metal,
    Subtitle,
)

# Adapted from
# https://gist.github.com/mayumi7/ca9e58a21459ccc76ee09873cff5000f
# https://forum.playboundless.com/t/documentation-of-itemcolorstrings-dat-structure/45708

LanguagePointer = namedtuple(
    "LanguagePointer", ("name", "start_index", "end_index")
)
ItemType = namedtuple("ItemType", ("item_id", "subtitle_id"))
GameItem = namedtuple("GameItem", ("name", "subtitle"))


def unpack_bits(binary, pointer, num_bits, count):
    values = []
    for i in range(count):
        offset = pointer + (i * num_bits // 8)
        bit_offset = i * num_bits % 8
        value = unpack_from("<I", binary, offset)[0]
        value = (value >> bit_offset) % pow(2, num_bits)
        values.append(value)

    return values


def decode_encodings(binary, pointer, index_count, final_index):
    length_lookup = [3, 6, 3, 10]

    encodings_pointer, words_index_pointer, words_pointer = unpack_from(
        "<III", binary, pointer
    )
    pointer += 12

    encoding_index_bits_per_value = unpack_from("B", binary, pointer)[0]
    pointer += 1

    encoding_index = unpack_bits(
        binary, pointer, encoding_index_bits_per_value, index_count
    )

    words_max_index = 0
    encodings = []
    for index in encoding_index:
        encoding_offset = 1
        encoding_pointer = encodings_pointer + index

        word_count_length = unpack_from("B", binary, encoding_pointer)[0] % 4
        word_count_length = length_lookup[word_count_length]

        if word_count_length > 3:
            encoding_offset += 1

        word_count = (
            unpack_from("<I", binary, encoding_pointer)[0] >> encoding_offset
        ) % pow(2, word_count_length)
        encoding_offset += word_count_length

        words = []

        while word_count > 0:
            word_offset = 1
            word_pointer = (
                encoding_pointer + (word_offset + encoding_offset) // 8
            )

            word_length = (
                unpack_from("<I", binary, word_pointer)[0]
                >> (encoding_offset % 8)
            ) % 4

            word_length = length_lookup[word_length]

            if word_length > 3:
                word_offset += 1

            word_index = (
                unpack_from("<I", binary, word_pointer)[0]
                >> ((word_offset + encoding_offset) % 8)
            ) % pow(2, word_length)

            if words_max_index < word_index:
                words_max_index = word_index

            words.append(word_index)
            encoding_offset += word_offset + word_length
            word_count -= 1

        encodings.append(words)

    words_max_index += 1

    words_index_bits_per_value = unpack_from("B", binary, words_index_pointer)[
        0
    ]
    words_index = unpack_bits(
        binary,
        words_index_pointer + 1,
        words_index_bits_per_value,
        words_max_index,
    )

    words = []
    total_words = len(words_index)
    for word_number, start_offset in enumerate(words_index):
        next_index = word_number + 1
        start_index = words_pointer + start_offset
        if next_index < total_words:
            letters = words_index[next_index] - start_offset
        else:
            letters = final_index - start_index

        words.append(
            unpack_from(f"<{letters}s", binary, start_index)[0].decode(
                "latin1"
            )
        )

    final_strings = []
    for encoding in encodings:
        final_strings.append(" ".join([words[i] for i in encoding]))

    return final_strings


def decode_index_data(binary):
    offset = 0
    metals_max_index = unpack_from("B", binary, offset)[0]
    offset += 1
    item_type_count = unpack_from("<H", binary, offset)[0]
    offset += 2

    item_types = []

    subtitles_max_index = -1

    for _ in range(item_type_count):
        item = ItemType(
            unpack_from("<H", binary, offset)[0],
            unpack_from("B", binary, offset + 2)[0],
        )
        if item[1] > subtitles_max_index:
            subtitles_max_index = item[1]
        item_types.append(item)
        offset += 3

    language_count = unpack_from("B", binary, offset)[0]
    offset += 1

    languages: List[LanguagePointer] = []
    for _ in range(language_count):
        language_name_length = unpack_from("B", binary, offset)[0]
        offset += 1

        language_name, language_address = unpack_from(
            f"<{language_name_length}sI", binary, offset
        )
        language_name = language_name.decode("ascii")
        offset += 4 + language_name_length

        if len(languages) > 0:
            languages[-1] = LanguagePointer(
                languages[-1].name,
                languages[-1].start_index,
                language_address,
            )
        languages.append(
            LanguagePointer(language_name, language_address, None)
        )

    languages[-1] = LanguagePointer(
        languages[-1].name, languages[-1].start_index, len(binary)
    )

    return metals_max_index, subtitles_max_index, item_types, languages


def decode_language(
    binary, num_metals, num_subtitles, num_colors, item_types, language,
):
    offset = language.start_index

    (
        color_strings_pointer,
        metal_strings_pointer,
        item_strings_pointer,
    ) = unpack_from("<III", binary, offset)
    offset += 12

    item_subtitles = decode_encodings(
        binary, offset, num_subtitles, color_strings_pointer
    )
    color_names = decode_encodings(
        binary, color_strings_pointer, num_colors, metal_strings_pointer
    )
    metal_names = decode_encodings(
        binary, metal_strings_pointer, num_metals, item_strings_pointer,
    )
    item_names = decode_encodings(
        binary, item_strings_pointer, len(item_types), language.end_index
    )

    color_strings: Dict[int, str] = {}
    for index, color_name in enumerate(color_names):
        color_strings[index + 1] = color_name

    metal_strings: Dict[int, str] = {}
    for index, metal_name in enumerate(metal_names):
        metal_strings[index] = metal_name

    item_strings: Dict[int, GameItem] = {}
    for index, item_type in enumerate(item_types):
        item_strings[item_type[0]] = GameItem(
            item_names[index], item_subtitles[item_type[1]]
        )

    return color_strings, metal_strings, item_strings


def construct_item_list(compileditems_binary):
    data = msgpack.unpackb(compileditems_binary, strict_map_key=False)

    items = {}
    for i in data[0].values():
        items[i[2]] = {
            data[1][2]: i[2],  # id
            data[1][10]: i[10],  # canDrop
            data[1][99]: i[99],  # stringID
        }

    return items


def print_result(name, created, action="imported"):
    if created > 0:
        click.echo(f"{action.title()} {created} new {name}(s)")
    else:
        click.echo(f"No new {name}s {action}")


@click.command()
@click.argument("itemcolorstrings_file", type=click.File("rb"), required=False)
@click.argument("compileditems_file", type=click.File("rb"), required=False)
def command(itemcolorstrings_file=None, compileditems_file=None):
    if itemcolorstrings_file is None:
        itemcolorstrings_file = open(settings.BOUNDLESS_ITEMS_FILE, "rb")
    if compileditems_file is None:
        compileditems_file = open(settings.BOUNDLESS_COMPILED_ITEMS_FILE, "rb")

    compiled_items = construct_item_list(compileditems_file.read())
    binary_data = itemcolorstrings_file.read()

    (
        metals_max_index,
        subtitles_max_index,
        item_types,
        languages,
    ) = decode_index_data(binary_data)

    click.echo(
        f"""Found
{metals_max_index+1} Metals
{subtitles_max_index+1} Item Subtitles
{len(item_types)} Items
{len(languages)} Languages
"""
    )

    click.echo("Creating Metals...")
    metals_created = 0
    metals = {}
    with click.progressbar(range(metals_max_index)) as bar:
        for index in bar:
            metal, was_created = Metal.objects.get_or_create(game_id=index)

            metals[metal.game_id] = metal

            if was_created:
                metals_created += 1
    print_result("metal", metals_created)

    click.echo("Creating Subtitles...")
    subtitles_created = 0
    subtitles = {}
    with click.progressbar(range(subtitles_max_index + 1)) as bar:
        for index in bar:
            subtitle, was_created = Subtitle.objects.get_or_create(
                game_id=index
            )

            subtitles[subtitle.game_id] = subtitle

            if was_created:
                subtitles_created += 1
    print_result("subtitle", subtitles_created)

    click.echo("Creating Items...")
    items_created = 0
    items_disabled = 0
    items = {}
    with click.progressbar(item_types) as bar:
        for item in bar:
            # do not add items that cannot be normally dropped
            if not compiled_items[item.item_id]["canDrop"]:
                items_disabled += Item.objects.filter(
                    game_id=item.item_id
                ).update(active=False)
                continue

            item_obj, was_created = Item.objects.get_or_create(
                game_id=item.item_id,
                string_id=compiled_items[item.item_id]["stringID"],
            )
            item_obj.item_subtitle = subtitles[item.subtitle_id]
            item_obj.save()

            items[item_obj.game_id] = item_obj

            if was_created:
                items_created += 1

    print_result("item", items_created)
    print_result("item", items_disabled, "disabled")

    click.echo("Creating Colors...")
    colors_created = 0
    colors = {}
    with click.progressbar(range(255)) as bar:
        for index in bar:
            color, was_created = Color.objects.get_or_create(game_id=index + 1)

            colors[color.game_id] = color

            if was_created:
                colors_created += 1
    print_result("color", colors_created)

    click.echo("Processing localization data...")

    for language in languages:
        click.echo(f"Creating localization data for {language.name}...")

        color_strings, metal_strings, item_strings = decode_language(
            binary_data,
            len(metals),
            len(subtitles),
            len(colors),
            item_types,
            language,
        )

        total = len(color_strings) + len(metal_strings) + len(item_strings)
        with click.progressbar(length=total) as bar:

            localizations_created = 0
            for index, name in color_strings.items():
                l, was_created = LocalizedName.objects.get_or_create(
                    game_obj=colors[index], lang=language.name
                )
                l.name = name
                l.save()

                if was_created:
                    localizations_created += 1

                bar.update(1)
                bar.render_progress()

            for index, name in metal_strings.items():
                l, was_created = LocalizedName.objects.get_or_create(
                    game_obj=metals[index], lang=language.name
                )
                l.name = name
                l.save()

                if was_created:
                    localizations_created += 1

                bar.update(1)
                bar.render_progress()

            for index, game_item in item_strings.items():
                bar.update(1)
                bar.render_progress()

                item = items.get(index)

                if item is None:
                    continue

                _, was_created = LocalizedName.objects.get_or_create(
                    game_obj=item, lang=language.name, name=game_item.name
                )

                if was_created:
                    localizations_created += 1

                l, was_created = LocalizedName.objects.get_or_create(
                    game_obj=item.item_subtitle, lang=language.name,
                )
                l.name = game_item.subtitle
                l.save()

                if was_created:
                    localizations_created += 1

        print_result("localization", localizations_created)
