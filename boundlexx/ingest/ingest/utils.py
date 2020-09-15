import djclick as click


def print_result(name, created, action="imported"):
    if created > 0:
        click.echo(f"{action.title()} {created} new {name}(s)")
    else:
        click.echo(f"No new {name} {action}")
