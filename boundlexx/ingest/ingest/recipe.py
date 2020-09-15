from typing import Dict, List, Optional

import djclick as click

from boundlexx.boundless.models import (
    Item,
    LocalizedString,
    Recipe,
    RecipeGroup,
    RecipeInput,
    RecipeLevel,
    RecipeRequirement,
    Skill,
)
from boundlexx.ingest.ingest.utils import print_result
from boundlexx.ingest.models import GameFile

SKILL_NAME_MAP = {"Forge Ingredient Crafting": "Forge Ingredients Crafting"}


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
    print_result("recipe groups", recipe_groups_created)


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

    return levels


def run():
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

    print_result("recipes", recipes_created)

    cleaned_up = 0
    cleaned_up += RecipeRequirement.objects.filter(recipe__isnull=True).delete()[0]
    cleaned_up += RecipeLevel.objects.filter(recipe__isnull=True).delete()[0]
    cleaned_up += RecipeInput.objects.filter(recipelevel__isnull=True).delete()[0]

    if cleaned_up > 0:
        click.echo(f"Cleaned up {cleaned_up} dangling recipe models")
