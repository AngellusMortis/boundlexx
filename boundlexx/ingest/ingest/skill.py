import djclick as click

from boundlexx.boundless.models import LocalizedString, Skill, SkillGroup
from boundlexx.ingest.ingest.icon import get_django_image, get_image
from boundlexx.ingest.ingest.utils import print_result
from boundlexx.ingest.models import GameFile


def _set_skill_attrs(skill, attrs):
    for attr_name, attr_value in attrs.items():
        if attr_name == "icon":
            if skill.icon is not None and skill.icon.name:
                skill.icon.delete()
            skill.icon = attr_value
        else:
            setattr(skill, attr_name, attr_value)


def run():
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
                name = f"{skill_dict['icon']}.png"
                image = get_image(f"gui/sprites/distance_maps_bw/icons/skills/{name}")

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
                    "icon": get_django_image(image, name),
                }

                skill, created = Skill.objects.get_or_create(
                    name=skill_dict["name"], defaults=attrs
                )

                if created:
                    skills_created += 1
                else:
                    _set_skill_attrs(skill, attrs)
                    skill.save()
        print_result("skill groups", skill_groups_created)
        print_result("skills", skills_created)
