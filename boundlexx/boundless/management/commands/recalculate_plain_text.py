# pylint: disable=protected-access
import parser
import re

import djclick as click
from django.db.models import Q
from django.utils.functional import SimpleLazyObject

from boundlexx.boundless.models import LocalizedStringText
from boundlexx.ingest.models import GameFile

ATTRIBUTES = [
    "Vitality",
    "Power",
    "Control",
    "Dexterity",
    "Agility",
    "Intelligence",
    "Luck",
    "Zeal",
    "Energy",
]

attributes = SimpleLazyObject(
    lambda: GameFile.objects.get(
        folder="assets/archetypes", filename="attributes.msgpack"
    ).content
)


def _get_modifier(bundles_to_check, target=None):
    for bundle in bundles_to_check:
        if target is None or bundle["target"] == target:
            mod_name = bundle["modifiers"][0]
            modifier = attributes["modifiers"][mod_name]
            modifier["name"] = mod_name
            return modifier

    return None


def _get_value_for_modifier(modifier):
    if modifier["type"] in ("add", "set"):  # pylint: disable=no-else-return
        return modifier["value"]
    elif modifier["type"] == "rel":
        return 1 + modifier["value"]
    return None


def _get_value_for_bundle(bundle_name, actions):
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


def _collapse_values(values):
    if isinstance(values, list):
        value_set = set()
        for v in values:
            value_set.add(v)

        if len(value_set) == 1:
            values = values[0]
    return values


def _format_value_list(values, display_type, multi_level, is_percent):
    formatted_values = []
    for v in values:
        formatted_values.append(_format_value(v, display_type, False, is_percent))

    value = _collapse_values(formatted_values)
    if isinstance(value, list):
        return "/".join(value)

    # multi level skills are additive
    if multi_level:
        value += " per level"
    return value


def _format_value(value, display_type, multi_level, is_percent):
    # pylint: disable=too-many-branches
    if isinstance(value, list):
        return _format_value_list(value, display_type, multi_level, is_percent)

    format_string = "{}"

    # int
    if display_type == 1:
        value = int(value)
    # percentages
    if is_percent or display_type in (2, 12) and isinstance(value, (int, float)):
        value = int(value * 100)
        if display_type == 12:
            format_string = "+{}%"
        else:
            format_string = "{}%"
    # health regen (25 per interval)
    elif display_type == 3:
        format_string = "25 per {}s"
    # speed
    elif display_type == 4:
        format_string = "{:.1}m/s"
    # distance
    elif display_type == 5:
        format_string = "{:.1}m"
    elif display_type == 7:
        format_string = "{} secs"
    # per s
    elif display_type == 15:
        format_string = "{} per s"
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


def _get_single_value_for_attribute(bundle_name, attribute_name):
    bundle = attributes["bundles"].get(bundle_name)
    if "bundles" in bundle:
        bundles = [attributes["bundles"][b] for b in bundle["bundles"]]
        modifier = _get_modifier(bundles, attribute_name)
    elif "modifiers" in bundle:
        modifier = _get_modifier([bundle])

    # cannot accurate display Post Relative attributes
    # without a real character
    if modifier["name"].startswith("Post Relative"):
        return None

    value = _get_value_for_modifier(modifier)
    return value


def _get_value_for_attribute(base_bundle_name, attribute_name, count, is_percent):
    if count > 1:
        values = []
        for x in range(count):
            bundle_name = f"{base_bundle_name} {x+1}"
            values.append(_get_single_value_for_attribute(bundle_name, attribute_name))
        value = _collapse_values(values)
    else:
        value = _get_single_value_for_attribute(base_bundle_name, attribute_name)

    # the ONE_BASED ones are really werid,
    # the base attribute is 0, but it seems to be additive on top of 1
    if is_percent and not count > 1:
        value = value + 1

    return value


def _get_args(match):
    match_type = match[0]
    args = match[1].split(",")

    name = args[0]
    extra = []
    if len(args) > 1:
        extra = args[1:]

    return match_type, name, extra


def _build_simple_list(st):
    stlist = []
    for i in st:
        if isinstance(i, str) and len(i) > 0:
            stlist.append(i)
        elif isinstance(i, list):
            stlist += _build_simple_list(i)
    return stlist


def _spacify(string):
    space_string = ""
    for char in string:
        if char.isupper():
            space_string += f" {char}"
        else:
            space_string += char
    return space_string.strip()


def _replace_constants(current_attribute, formula):
    formula = formula.replace(" ", "")
    parsed_formula = _build_simple_list(parser.st2list(parser.expr(formula)))

    replaced_formula = []
    for i in parsed_formula:
        # power operatior is differnt in Python
        if i == "^":
            i = "**"
        # interface for `round` is a little different
        elif i == "10":
            i = "-1"
        elif i == "0.01":
            i = "10"
        elif i == "ROUND":
            # Python round method is different
            i = "round"
        # operator/numbers
        elif len(i) > 1 and i != current_attribute:
            i = _spacify(i)

            char_attr = attributes["archetypes"]["Character"]["attributes"]
            if i in char_attr:
                i = _replace_constants(current_attribute, char_attr[i]["calculation"])
            else:
                i = str(attributes["constants"][i])
        replaced_formula.append(i)

    return "".join(replaced_formula)


def _calc(skill, count, input_base, raw_formula):
    current_attribute = skill.name if skill.name in ATTRIBUTES else None
    if current_attribute == "Zeal":
        current_attribute = "Energy"

    try:
        return float(raw_formula)
    except ValueError:
        pass

    base = attributes["constants"]["Attribute Base Value"]
    if raw_formula == "Attribute Base Value":
        return base

    formula = _replace_constants(current_attribute, raw_formula)

    abs_values = []
    for x in range(count):
        attribute_value = base + x * input_base

        f = formula
        if current_attribute is not None:
            f = f.replace(current_attribute, str(attribute_value))
        abs_values.append(eval(f))  # pylint: disable=eval-used  # nosec

    value = []
    for index, v in enumerate(abs_values):
        if index > 0:
            value.append(v - abs_values[index - 1])

    return value


def _replace_lookups(localization, matches):
    skill = localization.string.skill_set.first()
    if skill is None:
        return False

    changed = False

    for match in matches:
        match_type, name, extra = _get_args(match)
        value = None
        is_percent = False
        multi_level = skill.number_unlocks > 1
        attribute_name = None

        if match_type == "BUNDLE":
            value, attribute_name = _get_value_for_bundle(name, extra)
        elif match_type == "ATTRIBUTE":
            is_percent = "ONE_BASED" in extra
            attribute_name = name
            value = _get_value_for_attribute(
                skill.bundle_prefix, name, skill.number_unlocks, is_percent
            )

        elif match_type == "ACTION":
            value = name

        if value is not None:
            attribute = attributes["archetypes"]["Character"]["attributes"][
                attribute_name
            ]
            if attribute_name is not None:
                attr = _calc(
                    skill,
                    skill.number_unlocks + 1,
                    value,
                    attribute["calculation"],
                )
                if isinstance(attr, list):
                    value = attr

            value = _format_value(
                value, attribute["displayType"], multi_level, is_percent
            )

            localization._plain_text = localization._plain_text.replace(
                f"${{{match[0]}({match[1]})}}", value
            ).replace("per level Pts", "Pts per level")
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

    click.echo("Getting localizations that need processed...")
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
                changed = _replace_lookups(localized_text, matches)
            if changed:
                changed_count += 1
                localized_text.save()

    click.echo(f"{changed_count} of {total} updated")
