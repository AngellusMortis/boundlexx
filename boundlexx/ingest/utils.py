# pylint: skip-file

from collections import namedtuple
from struct import unpack_from
from typing import Dict, List

LanguagePointer = namedtuple("LanguagePointer", ("name", "start_index", "end_index"))


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
            word_pointer = encoding_pointer + (word_offset + encoding_offset) // 8

            word_length = (
                unpack_from("<I", binary, word_pointer)[0] >> (encoding_offset % 8)
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

    words_index_bits_per_value = unpack_from("B", binary, words_index_pointer)[0]
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
            unpack_from(f"<{letters}s", binary, start_index)[0].decode("latin1")
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
        item = {
            "item_id": unpack_from("<H", binary, offset)[0],
            "subtitle_id": unpack_from("B", binary, offset + 2)[0],
        }
        if item["subtitle_id"] > subtitles_max_index:
            subtitles_max_index = item["subtitle_id"]
        item_types.append(item)
        offset += 3

    language_count = unpack_from("B", binary, offset)[0]
    offset += 1

    languages: List[dict] = []
    for _ in range(language_count):
        language_name_length = unpack_from("B", binary, offset)[0]
        offset += 1

        language_name, language_address = unpack_from(
            f"<{language_name_length}sI", binary, offset
        )
        language_name = language_name.decode("ascii")
        offset += 4 + language_name_length

        if len(languages) > 0:
            languages[-1] = {
                "name": languages[-1]["name"],
                "start_index": languages[-1]["start_index"],
                "end_index": language_address,
            }
        languages.append(
            {
                "name": language_name,
                "start_index": language_address,
                "end_index": None,
            }
        )

    languages[-1] = {
        "name": languages[-1]["name"],
        "start_index": languages[-1]["start_index"],
        "end_index": len(binary),
    }

    return metals_max_index, subtitles_max_index, item_types, languages


def decode_language(
    binary,
    num_metals,
    num_subtitles,
    num_colors,
    item_types,
    language,
):
    offset = language["start_index"]

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
        binary,
        metal_strings_pointer,
        num_metals,
        item_strings_pointer,
    )
    item_names = decode_encodings(
        binary, item_strings_pointer, len(item_types), language["end_index"]
    )

    color_strings: Dict[int, str] = {}
    for index, color_name in enumerate(color_names):
        color_strings[index + 1] = color_name

    metal_strings: Dict[int, str] = {}
    for index, metal_name in enumerate(metal_names):
        metal_strings[index] = metal_name

    item_strings: Dict[int, dict] = {}
    for index, item_type in enumerate(item_types):
        item_strings[item_type["item_id"]] = item_names[index]

    subtitle_strings: Dict[int, str] = {}
    for index, subtitle_string in enumerate(item_subtitles):
        subtitle_strings[index] = subtitle_string

    return color_strings, metal_strings, item_strings, subtitle_strings


def decode_itemcolorstrings(binary_data):
    (
        metals_max_index,
        subtitles_max_index,
        item_types,
        languages,
    ) = decode_index_data(binary_data)

    data = {"items": item_types, "strings": {}}

    for language in languages:
        color_strings, metal_strings, item_strings, subtitle_strings = decode_language(
            binary_data,
            metals_max_index,
            subtitles_max_index + 1,
            255,
            item_types,
            language,
        )

        data["strings"][language["name"]] = {
            "colors": color_strings,
            "metals": metal_strings,
            "items": item_strings,
            "subtitles": subtitle_strings,
        }

    return data
