import djclick as click

from boundlexx.boundless.models import Color


def _create_color_group_data(colors: list[Color]):
    shades = {s: {s.value.lower()} for s in list(Color.ColorShade)}
    bases = {b: {b.value.lower()} for b in list(Color.ColorBase)}
    groups = {
        Color.ColorGroup.BLUE: {"azure", "cerulean", "cobalt", "blue"},
        Color.ColorGroup.VIOLET: {"lavender", "lilac", "magenta", "violet", "berry"},
        Color.ColorGroup.RED: {"fuchsia", "cherry", "red", "rose"},
        Color.ColorGroup.ORANGE: {"orange"},
        Color.ColorGroup.YELLOW: {"sepia", "taupe", "mustard", "tan", "yellow"},
        Color.ColorGroup.GREEN: {
            "lime",
            "moss",
            "green",
            "mint",
            "teal",
            "viridian",
            "turquoise",
            "slate",
        },
        Color.ColorGroup.BLACK: {"black", "grey", "white"},
    }

    bases[Color.ColorBase.BLACK].add("grey")
    bases[Color.ColorBase.BLACK].add("white")

    click.echo("Calculating color groups...")
    with click.progressbar(colors) as pbar:
        for color in pbar:
            parts = set(color.default_name.lower().split(" "))

            for shade, values in shades.items():
                if len(parts & values) > 0:
                    color.shade = shade
                    break

                if len(parts) == 1:
                    color.shade = Color.ColorShade.PURE
                    break

            for base, values in bases.items():
                if len(parts & values) > 0:
                    color.base = base
                    break

            if color.base is None:
                click.echo(f"Could not find base for {color}")

            for group, values in groups.items():
                if len(parts & values) > 0:
                    color.group = group
                    break

            if color.group is None:
                click.echo(f"Could not find group for {color}")

            color.save()


def run(force=False, **kwargs):
    _create_color_group_data(Color.objects.all())
