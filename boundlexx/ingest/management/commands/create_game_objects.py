from importlib import import_module

import djclick as click

BASE = "boundlexx.ingest.ingest"


@click.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force replace images",
)
@click.option(
    "--skip-variants",
    is_flag=True,
    help="Skips color variants",
)
@click.option(
    "--start-item-id",
    type=int,
    help="Starting ID for Item group",
)
@click.option(
    "--end-item-id",
    type=int,
    help="Ending ID for Item group",
)
@click.option(
    "-c",
    "--core",
    is_flag=True,
    help="Run all core group (Metals/Items/Subtitles/Localization Data",
)
@click.option(
    "-r",
    "--recipe",
    is_flag=True,
    help="Crafting Recipes group",
)
@click.option(
    "-i",
    "--item",
    is_flag=True,
    help="Item group. Second pass to add localizations and images to items",
)
@click.option(
    "-o",
    "--resources",
    is_flag=True,
    help="Resources group",
)
@click.option(
    "-s",
    "--skill",
    is_flag=True,
    help="Skill Tree group",
)
@click.option(
    "-e",
    "--emoji",
    is_flag=True,
    help="Emojis group",
)
def command(force, start_item_id, end_item_id, skip_variants, **kwargs):
    if not any(kwargs.values()):
        for index in kwargs:
            kwargs[index] = True

    for index, value in kwargs.items():
        if value:
            module = import_module(f"{BASE}.{index}")
            module.run(  # type: ignore
                force=force,
                start_id=start_item_id,
                end_id=end_item_id,
                color_variants=(not skip_variants),
            )
