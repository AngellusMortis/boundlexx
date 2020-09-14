# pylint: disable=protected-access
import re

import djclick as click
from django.db.models import Q

from boundlexx.boundless.models import LocalizedStringText
from boundlexx.ingest.models import GameFile


def _get_modifier(attributes, bundles_to_check, target=None):
    for bundle in bundles_to_check:
        if target is None or bundle["target"] == target:
            mod_name = bundle["modifiers"][0]
            modifier = attributes["modifiers"][mod_name]
            modifier["name"] = mod_name
            return modifier

    return None


def _get_value_for_modifier(modifier):
    if modifier["type"] in ("add", "rel", "set"):
        return modifier["value"]
    return None


def _get_value_for_bundle(attributes, bundle_name, actions):
    bundle = attributes["bundles"].get(bundle_name)
    if bundle is None or "modifiers" not in bundle:
        return None

    attribute_name = bundle["target"]
    modifier = attributes["modifiers"][bundle["modifiers"][0]]
    value = _get_value_for_modifier(modifier)

    if value is not None:
        if "ABS" in actions:
            value = abs(value)

        if "MUL" in actions:
            value = f"x{value}"
        elif "VAL" not in actions:
            value = None
    return value, attribute_name


def _format_value(value, display_type, multi_level, is_percent):
    format_string = "{}"
    # percentages
    if is_percent or display_type in (2, 12):
        value = int(value * 100)
        format_string = "{}%"
    # health regen (25 per interval)
    elif display_type == 3:
        format_string = "25 per {}s"
    # speed
    elif display_type == 4:
        format_string = "{}m/s"
    # distance
    elif display_type == 5:
        format_string = "{}m"
    elif display_type == 7:
        format_string = "{} secs"
    # large number (add commas)
    elif display_type == 15:
        format_string = "{:,d}"
    elif display_type == 19:
        if value == 2:
            value = "doubles"
        else:
            value = None

    # multi level skills are additive
    if multi_level:
        format_string += " per level"

    if value is not None:
        value = format_string.format(value)
    return value


def _get_value_for_attribute(
    attributes, bundle_name, attribute_name, multi_level, is_percent
):
    bundle = attributes["bundles"].get(bundle_name)
    if "bundles" in bundle:
        bundles = [attributes["bundles"][b] for b in bundle["bundles"]]
        modifier = _get_modifier(attributes, bundles, attribute_name)
    elif "modifiers" in bundle:
        modifier = _get_modifier(attributes, [bundle])

    # cannot accurate display Post Relative attributes
    # without a real character
    if modifier["name"].startswith("Post Relative"):
        return None

    value = _get_value_for_modifier(modifier)
    return value


def _get_args(match):
    match_type = match[0]
    args = match[1].split(",")

    name = args[0]
    extra = []
    if len(args) > 1:
        extra = args[1:]

    return match_type, name, extra


def _replace_lookups(attributes, localization, matches):
    skill = localization.string.skill_set.first()
    if skill is None:
        return False

    changed = False

    for match in matches:
        match_type, name, extra = _get_args(match)
        value = None
        is_percent = False
        multi_level = skill.number_unlocks > 1

        if match_type == "BUNDLE":
            value, attribute_name = _get_value_for_bundle(attributes, name, extra)
        elif match_type == "ATTRIBUTE":
            is_percent = "ONE_BASED" in extra
            bundle_name = skill.bundle_prefix
            if multi_level:
                bundle_name = f"{bundle_name} 1"

            value = _get_value_for_attribute(
                attributes, bundle_name, name, multi_level, is_percent
            )
            attribute_name = name
        elif match_type == "ACTION":
            value = name

        if value is not None:
            attribute = attributes["archetypes"]["Character"]["attributes"][
                attribute_name
            ]
            value = _format_value(
                value, attribute["displayType"], multi_level, is_percent
            )

            localization._plain_text = localization._plain_text.replace(
                f"${{{match[0]}({match[1]})}}", value
            )
            changed = True

    return changed


@click.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Clear existing",
)
def command(force):
    if force:
        LocalizedStringText.objects.all().update(
            _plain_text=None,
        )

    texts = (
        LocalizedStringText.objects.filter(
            Q(_plain_text__isnull=True)
            | Q(_plain_text__contains="ATTRIBUTE")
            | Q(_plain_text__contains="BUNDLE")
            | Q(_plain_text__contains="ACTION")
        )
        .select_related("string")
        .prefetch_related("string__skill_set")
    )
    total = texts.count()
    changed_count = 0

    click.echo("Getting localizations that need processed...")
    attributes_file = GameFile.objects.filter(
        folder="assets/archetypes", filename="attributes.msgpack"
    ).first()
    if attributes_file is None:
        return
    attributes = attributes_file.content

    with click.progressbar(texts) as pbar:
        for localized_text in pbar:
            changed = False

            if localized_text._plain_text is None:
                localized_text._plain_text = re.sub(
                    LocalizedStringText.STYLE_REGEX,
                    r"\g<1>",
                    localized_text.text,
                )
                localized_text._plain_text = re.sub(
                    LocalizedStringText.POST_REL_REGEX,
                    r"",
                    localized_text._plain_text,
                )
                changed = True

            matches = re.findall(
                LocalizedStringText.ATTRIBUTE_REGEX, localized_text._plain_text
            )

            if len(matches) > 0:
                changed = _replace_lookups(attributes, localized_text, matches)
            if changed:
                changed_count += 1
                localized_text.save()

    click.echo(f"{changed_count} of {total} updated")
