import os
from io import BytesIO

import djclick as click
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

from boundlexx.api.tasks import purge_static_cache
from boundlexx.boundless.models import (
    AltItem,
    Block,
    Color,
    Item,
    ItemColorVariant,
    ItemMetalVariant,
    Liquid,
    LocalizedString,
    Metal,
    Recipe,
)
from boundlexx.ingest.models import GameFile
from boundlexx.utils import make_thumbnail


def _blocks(compiled_blocks, items):
    click.echo("Generating block mappings...")
    blocks_created = 0
    with click.progressbar(compiled_blocks["BlockTypesData"]) as pbar:
        for block_data in pbar:
            if block_data is None:
                continue

            item = None
            item_id = (
                block_data["inventoryRemap"]
                or block_data["rootType"]
                or block_data["id"]
            )
            if item_id != 0:
                item = items.get(item_id)

            if item is None:
                item = Item.objects.filter(
                    string_id=f"ITEM_TYPE_{block_data['name']}"
                ).first()

            if item is not None:
                item.is_block = True
                item.prestige = block_data.get("prestige", 0)
                item.mine_xp = block_data.get("mineXP", 0)
                item.build_xp = block_data.get("buildXP", 0)
                item.save()

            _, created = Block.objects.get_or_create(
                game_id=block_data["id"], name=block_data["name"], block_item=item
            )

            if created:
                blocks_created += 1


def _liquids(compiled_blocks, items):
    click.echo("Generating liquid mappings...")
    liquids_created = 0
    with click.progressbar(compiled_blocks["LiquidTypesData"].values()) as pbar:
        for liquid_data in pbar:
            if liquid_data is None:
                continue

            item = None
            item_id = liquid_data["itemType"]
            if item_id != 0:
                item = items.get(item_id)

            if item is None:
                item = Item.objects.filter(
                    string_id=f"ITEM_TYPE_{liquid_data['name']}"
                ).first()

            if item is not None:
                item.is_liquid = True
                item.prestige = liquid_data.get("prestige", 0)
                item.mine_xp = liquid_data.get("mineXP", 0)
                item.build_xp = liquid_data.get("buildXP", 0)
                item.save()

            _, created = Liquid.objects.get_or_create(
                game_id=liquid_data["id"], name=liquid_data["name"], block_item=item
            )

            if created:
                liquids_created += 1

    click.echo(f"{liquids_created} Liquid(s) created")


def _crop_image(image_path, name):
    img = Image.open(image_path)

    # crop to bounding box
    try:
        x1, y1, x2, y2 = img.getbbox()
    except TypeError:
        return None
    img = img.crop((x1 - 5, y1 - 5, x2 + 5, y2 + 5))

    # make square
    x, y = img.size
    width = max(x, y)
    new_img = Image.new("RGBA", (width, width), (0, 0, 0, 0))
    new_img.paste(img, (int((width - x) / 2), int((width - y) / 2)))

    image_content = BytesIO()
    new_img.save(image_content, format="PNG")

    image = ContentFile(image_content.getvalue())
    image.name = f"{name}.png"

    return image


def _create_color_icons(force, item, image_dir, pbar):
    ItemMetalVariant.objects.filter(item=item).delete()

    if force:
        existing_colors = []

        variants = ItemColorVariant.objects.filter(item=item)
        for v in variants:
            v.image.delete()
            if v.image_small is not None and v.image_small.name:
                v.image_small.delete()
        variants.delete()
    else:
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
            image = _crop_image(image_path, f"{item.game_id}_{color.game_id}")
            ItemColorVariant.objects.create(
                item=item,
                color=color,
                image=image,
                image_small=make_thumbnail(image),
            )


def _create_metal_icons(force, item, image_dir, pbar):
    ItemColorVariant.objects.filter(item=item).delete()

    if force:
        existing_colors = []

        variants = ItemMetalVariant.objects.filter(item=item)
        for v in variants:
            v.image.delete()
            if v.image_small is not None and v.image_small.name:
                v.image_small.delete()
        variants.delete()
    else:
        existing_colors = [
            i.metal.game_id for i in ItemMetalVariant.objects.filter(item=item)
        ]

    for metal in Metal.objects.exclude(game_id__in=existing_colors):
        pbar.label = f"{item.game_id}:{metal.game_id}"
        pbar.render_progress()

        image_path = os.path.join(image_dir, f"{metal}_{metal.game_id}.png")
        if not os.path.isfile(image_path):
            image_path = os.path.join(image_dir, f"{metal}_0.png")

        if os.path.isfile(image_path):
            image = _crop_image(image_path, f"{item.game_id}_{metal.game_id}")
            ItemMetalVariant.objects.create(
                item=item,
                metal=metal,
                image=image,
                image_small=make_thumbnail(image),
            )


def _get_default_image(image_dir, item):
    has_colors = os.path.isfile(os.path.join(image_dir, "10_0.png"))
    if has_colors:
        item.default_color = _get_default_color(item)
        default_image = os.path.join(image_dir, f"{item.default_color.game_id-1}_0.png")
    else:
        default_image = os.path.join(image_dir, "0_0.png")

    return default_image


def _create_icons(item, pbar, force=False, color_variants=True):
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
        default_image = _get_default_image(image_dir, item)

        if os.path.isfile(default_image) and (
            force or item.image is None or not item.image.name
        ):
            if item.image is not None and item.image.name:
                item.image.delete()
            item.image = _crop_image(default_image, f"{item.game_id}")

            if item.image is None:
                click.echo(f"Invalid image file: {default_image}")
                return

            if item.image_small is not None and item.image_small.name:
                item.image_small.delete()
            item.image_small = make_thumbnail(item.image)

    if color_variants and os.path.isfile(os.path.join(image_dir, "1_0.png")):
        if os.path.isfile(os.path.join(image_dir, "10_0.png")):
            _create_color_icons(force, item, image_dir, pbar)
        else:
            _create_metal_icons(force, item, image_dir, pbar)


def _get_default_color(item):
    source_item = item
    found = False
    while not found:
        try:
            recipe = Recipe.objects.get(output=source_item)
        except Recipe.DoesNotExist:
            found = True
        else:
            source_item = recipe.tints.first()

    try:
        default_color_id = settings.BOUNDLESS_DEFAULT_COLORS[source_item.game_id]
    except KeyError:
        if "IGNEOUS" in source_item.name:
            default_color_id = settings.BOUNDLESS_DEFAULT_COLORS[10798]
        elif "SEDIMENTARY" in source_item.name:
            default_color_id = settings.BOUNDLESS_DEFAULT_COLORS[10802]
        elif "ROCK" in source_item.name or "SEAM_DUGUP" in source_item.item.name:
            default_color_id = settings.BOUNDLESS_DEFAULT_COLORS[10802]
        elif "GNARLED" in source_item.name:
            default_color_id = settings.BOUNDLESS_DEFAULT_COLORS[6157]
        elif "BARBED" in source_item.name:
            default_color_id = settings.BOUNDLESS_DEFAULT_COLORS[3085]
        elif "VERDANT" in source_item.name:
            default_color_id = settings.BOUNDLESS_DEFAULT_COLORS[13]
        else:
            raise

    return Color.objects.get(game_id=default_color_id)


def run(  # pylint: disable=too-many-locals
    force=False, start_id=None, end_id=None, color_variants=True, **kwargs
):
    items = {}

    compiled_items = GameFile.objects.get(
        folder="assets/archetypes", filename="compileditems.msgpack"
    ).content

    items_query = Item.objects.all()
    if start_id is not None:
        items_query = items_query.filter(game_id__gte=start_id)

    if end_id is not None:
        items_query = items_query.filter(game_id__lte=end_id)

    click.echo("Attaching localization and images data to items...")
    with click.progressbar(
        items_query.iterator(),
        show_percent=True,
        show_pos=True,
        length=items_query.count(),
    ) as pbar:
        for item in pbar:
            pbar.label = str(item.game_id)
            pbar.render_progress()

            items[item.game_id] = item
            list_type = compiled_items[str(item.game_id)].get("listTypeName")

            if list_type:
                item.list_type = LocalizedString.objects.filter(
                    string_id=list_type
                ).first()
            item.description = LocalizedString.objects.filter(
                string_id=f"{item.string_id}_DESCRIPTION"
            ).first()
            _create_icons(item, pbar, force, color_variants)
            item.save()

    click.echo("Purging CDN cache...")
    purge_static_cache()

    click.echo("Creating AltItems...")
    with click.progressbar(compiled_items.items()) as pbar:
        for item_id, item_data in pbar:
            item_id = int(item_id)

            if item_id in items:
                continue

            string_id = item_data["stringID"]
            if "ITEM_TYPE_ASH_RECLAIM" in string_id:
                string_id = "ITEM_TYPE_ASH_DEFAULT_BASE"

            item = Item.objects.filter(string_id=string_id).first()

            if item is not None:
                alt_item, _ = AltItem.objects.get_or_create(
                    game_id=int(item_data["id"]), name=item_data["name"], base_item=item
                )

                items[alt_item.game_id] = item

    compiled_blocks = GameFile.objects.get(
        folder="assets/archetypes", filename="compiledblocks.msgpack"
    ).content

    _blocks(compiled_blocks, items)
    _liquids(compiled_blocks, items)
