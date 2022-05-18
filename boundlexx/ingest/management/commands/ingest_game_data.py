import json
import os
from typing import Optional, Union

import djclick as click
import msgpack
import semver
from django.conf import settings

from boundlexx.ingest.models import GameFile
from boundlexx.ingest.utils import decode_itemcolorstrings


def _parse_json_file(filepath):
    with open(filepath, "r", encoding="utf8") as f:
        json_content = json.load(f)

    return json_content


def _clean_msgpack_value(value, lookup):
    if isinstance(value, (dict, list)):
        value = _map_msgpack(value, lookup)
    elif isinstance(value, str):
        value = value.replace("\u0000", "")

    return value


def _map_msgpack(unmapped, lookup):
    mapped: Optional[Union[list, dict]] = None
    if isinstance(unmapped, dict):
        mapped = {}

        for key, value in unmapped.items():
            value = _clean_msgpack_value(value, lookup)
            mapped[lookup[key]] = value
    elif isinstance(unmapped, list):
        mapped = []
        for value in unmapped:
            value = _clean_msgpack_value(value, lookup)
            mapped.append(value)
    else:
        raise Exception("Unknown unmapped object")

    return mapped


def _parse_msgpack_file(filepath):
    with open(filepath, "rb") as f:
        binary_data = f.read()

    try:
        root, lookup = msgpack.unpackb(binary_data, strict_map_key=False)
    except UnicodeDecodeError:
        click.secho(f"Could not decode {filepath}", fg="yellow")
        return None

    return _map_msgpack(root, lookup)


def _parse_itemcolorstrings(filepath):
    with open(filepath, "rb") as f:
        binary_data = f.read()

    return decode_itemcolorstrings(binary_data)


def _process_file(root, filename, game_version):
    gamefolder = root.replace(settings.BOUNDLESS_LOCATION, "")
    filepath = os.path.join(root, filename)

    json_content = None
    file_type = GameFile.Filetype.OTHER

    game_file = (
        GameFile.objects.filter(folder=gamefolder, filename=filename)
        .order_by("-id")
        .first()
    )
    version_compare = (
        game_version.compare(game_file.game_version) if game_file is not None else None
    )

    if version_compare is not None and version_compare < 1:
        click.echo(f"Skipping {filepath}...")
    elif filename.endswith(".json"):
        json_content = _parse_json_file(filepath)
        file_type = GameFile.Filetype.JSON
    elif filename.endswith(".msgpack"):
        json_content = _parse_msgpack_file(filepath)
        file_type = GameFile.Filetype.MSGPACK
    elif gamefolder == "assets/archetypes" and filename == "itemcolorstrings.dat":
        json_content = _parse_itemcolorstrings(filepath)

    if json_content:
        if game_file is not None:
            if version_compare == 1 and game_file.content != json_content:
                click.secho(f"New version of {filepath}...")
                game_file.delete()
                game_file = None

        if game_file is not None:
            click.echo(f"Skipping {filepath}...")
            return

        click.secho(f"Importing {filepath}...", fg="green")
        GameFile.objects.create(
            folder=gamefolder,
            filename=filename,
            content=json_content,
            file_type=file_type,
            game_version=str(game_version),
        )


@click.command()
@click.argument("game_version", type=str, required=True)
@click.option("-f", "--file_path", type=click.Path(exists=True))
def command(game_version, file_path):
    game_version = semver.VersionInfo.parse(game_version)

    if file_path is not None:
        _process_file(
            os.path.dirname(file_path), os.path.basename(file_path), game_version
        )
        return

    for root, _, files in os.walk(settings.BOUNDLESS_LOCATION):
        for filename in files:
            _process_file(root, filename, game_version)
