from typing import Dict, List, Optional

import djclick as click

from boundlexx.boundless.models import (
    Color,
    ColorValue,
    Item,
    LocalizedName,
    LocalizedString,
    LocalizedStringText,
    Metal,
    Recipe,
    RecipeGroup,
    RecipeInput,
    RecipeLevel,
    RecipeRequirement,
    Skill,
    SkillGroup,
    Subtitle,
)
from boundlexx.ingest.models import GameFile

SKILL_NAME_MAP = {"Forge Ingredient Crafting": "Forge Ingredients Crafting"}


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
            item_obj.name = compiled_items[string_item_id]["name"]
            item_obj.item_subtitle = subtitles[item["subtitle_id"]]
            item_obj.mint_value = compiled_items[string_item_id]["coinValue"]

            # items that cannot be dropped or minted are not normally obtainable
            can_drop = compiled_items[string_item_id]["canDrop"]
            is_active = can_drop and item_obj.mint_value is not None

            if not was_created and (not is_active and item_obj.active):
                items_disabled += 1
            item_obj.active = is_active
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
    _print_result("localized names", localizations_created)


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
        _print_result("localized strings", strings_created)


def _core_group():
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


def _item_group():
    click.echo("Attaching localization data to items...")
    compiled_items = GameFile.objects.get(
        folder="assets/archetypes", filename="compileditems.msgpack"
    ).content
    with click.progressbar(Item.objects.all()) as pbar:
        for item in pbar:
            list_type = compiled_items[str(item.game_id)].get("listTypeName")

            if list_type:
                item.list_type = LocalizedString.objects.filter(
                    string_id=list_type
                ).first()
            item.description = LocalizedString.objects.filter(
                string_id=f"{item.string_id}_DESCRIPTION"
            ).first()
            item.save()


def _skill_group():
    skilltrees = GameFile.objects.get(
        folder="assets/archetypes", filename="skilltrees.msgpack"
    ).content

    click.echo("Importing skills...")
    with click.progressbar(skilltrees.items()) as pbar:
        skill_groups_created = 0
        skills_created = 0

        for skill_group_name, skill_group_dict in pbar:
            attrs = {
                "skill_type": skill_group_dict["type"],
                "display_name": LocalizedString.objects.get(
                    string_id=skill_group_dict["displayName"]
                ),
                "unlock_level": skill_group_dict["unlockAtLevel"],
            }

            skill_group, created = SkillGroup.objects.get_or_create(
                name=skill_group_name, defaults=attrs
            )

            if created:
                skill_groups_created += 1
            else:
                for attr_name, attr_value in attrs.items():
                    setattr(skill_group, attr_name, attr_value)
                skill_group.save()

            for skill_dict in skill_group_dict["skills"]:
                attrs = {
                    "group": skill_group,
                    "number_unlocks": skill_dict["num"],
                    "cost": skill_dict["cost"],
                    "order": skill_dict["order"],
                    "category": skill_dict["category"],
                    "link_type": skill_dict["linkType"],
                    "description": LocalizedString.objects.get(
                        string_id=skill_dict["description"]
                    ),
                    "display_name": LocalizedString.objects.get(
                        string_id=skill_dict["displayName"]
                    ),
                    "bundle_prefix": skill_dict["bundlePrefix"],
                    "affected_by_other_skills": skill_dict["affectedByOtherSkills"],
                }

                skill, created = Skill.objects.get_or_create(
                    name=skill_dict["name"], defaults=attrs
                )

                if created:
                    skills_created += 1
                else:
                    for attr_name, attr_value in attrs.items():
                        setattr(skill, attr_name, attr_value)
                    skill.save()
        _print_result("skill groups", skill_groups_created)
        _print_result("skills", skills_created)


def _create_recipe_groups(recipes):
    recipe_groups_created = 0
    click.echo("Importing recipe groups...")
    with click.progressbar(recipes["groups"]) as pbar:
        for group in pbar:
            display_name = LocalizedString.objects.get(
                string_id=group["groupDisplayName"]
            )
            recipe_group, created = RecipeGroup.objects.get_or_create(
                name=group["groupName"], defaults={"display_name": display_name}
            )

            members = []
            for member_id in group["groupMembers"]:
                members.append(Item.objects.get(game_id=member_id))
            recipe_group.members.set(members)

            if created:
                recipe_groups_created += 1
            else:
                recipe_group.display_name = display_name
                recipe_group.save()
    _print_result("recipe groups", recipe_groups_created)


def _get_tints(item_ids):
    tints = []
    for item_id in item_ids:
        tints.append(Item.objects.get(game_id=item_id))

    return tints


def _get_requirements(requirements_list):
    requirements = []
    for skill_dict in requirements_list:
        skill_name = skill_dict["attribute"][:-6]
        skill_name = SKILL_NAME_MAP.get(skill_name, skill_name)

        requirement, _ = RecipeRequirement.objects.get_or_create(
            skill=Skill.objects.get(name=skill_name),
            level=skill_dict["level"],
        )

        requirements.append(requirement)

    return requirements


def _get_inputs(inputs_list):
    inputs: Dict[RecipeLevel.Level, List[RecipeInput]] = {
        RecipeLevel.Level.SINGLE: [],
        RecipeLevel.Level.BULK: [],
        RecipeLevel.Level.MASS: [],
    }
    for input_dict in inputs_list:
        group: Optional[RecipeGroup] = None
        item: Optional[Item] = None

        if "groupId" in input_dict:
            group = RecipeGroup.objects.get(name=input_dict["groupId"])
        elif len(input_dict["inputItems"]) > 1:
            raise Exception("Too many inputs")
        else:
            item = Item.objects.get(game_id=input_dict["inputItems"][0])

        for index, count in enumerate(input_dict["inputQuantity"]):
            rinput, _ = RecipeInput.objects.get_or_create(
                group=group, item=item, count=count
            )
            inputs[index].append(rinput)  # type: ignore

    return inputs


def _get_levels(recipe_dict):
    inputs = _get_inputs(recipe_dict["inputs"])

    levels = []
    for level, linputs in inputs.items():
        kwargs = {
            "level": level,
            "wear": recipe_dict["wear"][level],
            "spark": recipe_dict["spark"][level],
            "duration": recipe_dict["duration"][level],
            "output_quantity": recipe_dict["outputQuantity"][level],
        }

        recipe_levels = RecipeLevel.objects.filter(**kwargs).prefetch_related("inputs")

        incoming_ids = sorted(r.id for r in linputs)
        recipe_level = None
        for rlevel in recipe_levels:
            compare_ids = sorted(r.id for r in rlevel.inputs.all())

            if incoming_ids == compare_ids:
                recipe_level = rlevel

        if recipe_level is None:
            recipe_level = RecipeLevel.objects.create(**kwargs)
            recipe_level.inputs.set(linputs)
        levels.append(recipe_level)


def _recipe_group():
    recipes = GameFile.objects.get(
        folder="assets/archetypes", filename="recipes.msgpack"
    ).content

    _create_recipe_groups(recipes)

    recipes_created = 0
    click.echo("Importing crafting recipes...")
    with click.progressbar(recipes["recipes"]) as pbar:
        for recipe_dict in pbar:
            attrs = {
                "heat": recipe_dict["heat"],
                "craft_xp": recipe_dict["craftXP"],
                "machine": recipe_dict.get("machine"),
                "output": Item.objects.get(game_id=recipe_dict["outputItem"]),
                "can_hand_craft": recipe_dict["canHandCraft"],
                "machine_level": recipe_dict["machineLevel"],
                "power": recipe_dict["powerRequired"],
                "group_name": recipe_dict["recipeGroupName"],
                "knowledge_unlock_level": recipe_dict["knowledgeUnlockLevel"],
            }
            recipe, created = Recipe.objects.get_or_create(
                game_id=recipe_dict["ID"], defaults=attrs
            )

            recipe.tints.set(_get_tints(recipe_dict["tintTakenFrom"]))
            recipe.requirements.set(
                _get_requirements(recipe_dict.get("prerequisites", []))
            )
            recipe.levels.set(_get_levels(recipe_dict))

            if created:
                recipes_created += 1
            else:
                for attr_name, attr_value in attrs.items():
                    setattr(recipe, attr_name, attr_value)
                recipe.save()

    _print_result("recipes", recipes_created)

    cleaned_up = 0
    cleaned_up += RecipeRequirement.objects.filter(recipe__isnull=True).delete()[0]
    cleaned_up += RecipeLevel.objects.filter(recipe__isnull=True).delete()[0]
    cleaned_up += RecipeInput.objects.filter(recipelevel__isnull=True).delete()[0]

    if cleaned_up > 0:
        click.echo(f"Cleaned up {cleaned_up} dangling recipe models")


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
def command(core, item, skill, recipe):
    if not any([core, item, skill, recipe]):
        core = True

    if core:
        _core_group()

    if item:
        _item_group()

    if skill:
        _skill_group()

    if recipe:
        _recipe_group()
