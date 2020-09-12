import djclick as click

from boundlexx.boundless.models import (
    Color,
    ColorValue,
    Item,
    LocalizedName,
    Metal,
    Subtitle,
)
from boundlexx.ingest.models import GameFile


def _print_result(name, created, action="imported"):
    if created > 0:
        click.echo(f"{action.title()} {created} new {name}(s)")
    else:
        click.echo(f"No new {name} {action}")


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
    _print_result(name, created)

    return objects


def _create_items(items_list, subtitles):
    compiled_items = GameFile.objects.get(
        folder="assets/archetypes", filename="compileditems.msgpack"
    ).content

    click.echo("Creating Items...")
    items_created = 0
    items_disabled = 0
    items = {}
    with click.progressbar(items_list) as pbar:
        for item in pbar:
            string_item_id = str(item["item_id"])

            item_obj, was_created = Item.objects.get_or_create(
                game_id=item["item_id"],
                string_id=compiled_items[string_item_id]["stringID"],
            )
            item_obj.item_subtitle = subtitles[item["subtitle_id"]]

            # items that cannot be normally dropped should not be active
            can_drop = compiled_items[string_item_id]["canDrop"]
            if not was_created and (not can_drop and item_obj.active):
                items_disabled += 1
            item_obj.active = can_drop
            item_obj.save()

            items[item_obj.game_id] = item_obj

            if was_created:
                items_created += 1
    _print_result("item", items_created)
    _print_result("item", items_disabled, "disabled")

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
    _print_result("color values", color_values_created)

    return colors


def _create_localization_data(strings, metals, subtitles, items, colors):
    click.echo("Processing localization data...")
    for lang_name, lang_data in strings.items():
        click.echo(f"Creating localization data for {lang_name}...")

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
                    game_obj=colors[int(index)], lang=lang_name
                )
                l.name = name
                l.save()

                if was_created:
                    localizations_created += 1

                pbar.update(1)
                pbar.render_progress()

            for index, name in lang_data["metals"].items():
                l, was_created = LocalizedName.objects.get_or_create(
                    game_obj=metals[int(index)], lang=lang_name
                )
                l.name = name
                l.save()

                if was_created:
                    localizations_created += 1

                pbar.update(1)
                pbar.render_progress()

            for index, name in lang_data["items"].items():
                l, was_created = LocalizedName.objects.get_or_create(
                    game_obj=items[int(index)], lang=lang_name
                )
                l.name = name
                l.save()

                if was_created:
                    localizations_created += 1

                pbar.update(1)
                pbar.render_progress()

            for index, name in lang_data["subtitles"].items():
                l, was_created = LocalizedName.objects.get_or_create(
                    game_obj=subtitles[int(index)], lang=lang_name
                )
                l.name = name
                l.save()

                if was_created:
                    localizations_created += 1

                pbar.update(1)
                pbar.render_progress()
        _print_result("localization", localizations_created)


@click.command()
def command():
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

    metals = _create_generic(
        "Metals", strings["strings"]["english"]["metals"].keys(), Metal
    )
    subtitles = _create_generic(
        "Subtitles", strings["strings"]["english"]["subtitles"].keys(), Subtitle
    )
    items = _create_items(strings["items"], subtitles)
    colors = _create_colors(strings["strings"]["english"]["colors"].keys())

    _create_localization_data(strings["strings"], metals, subtitles, items, colors)
