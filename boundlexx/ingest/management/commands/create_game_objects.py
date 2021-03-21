from importlib import import_module

import djclick as click

BASE = "boundlexx.ingest.ingest"


@click.command()
@click.option(
    "-c",
    "--core",
    is_flag=True,
    help="Run all core group (Metals/Items/Subtitles/Localization Data",
)
@click.option(
    "-i",
    "--item",
    is_flag=True,
    help="Item localiazation group. Second pass to add localization strings to items",
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
    "-r",
    "--recipe",
    is_flag=True,
    help="Crafting Recipes group",
)
@click.option(
    "-e",
    "--emoji",
    is_flag=True,
    help="Emojis group",
)
def command(**kwargs):
    if not any(kwargs.values()):
        for index in kwargs:
            kwargs[index] = True

    for index, value in kwargs.items():
        if value:
            module = import_module(f"{BASE}.{index}")
            module.run()  # type: ignore
