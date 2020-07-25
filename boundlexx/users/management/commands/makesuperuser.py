import djclick as click
from django.contrib.auth import get_user_model

User = get_user_model()


@click.command()
@click.option("--username", prompt=True)
def command(username: str):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        click.secho(f"{username} does not exist", fg="red")
    else:
        user.is_staff = True
        user.is_superuser = True
        user.save()
        click.secho(f"{username} has been made a superuser", fg="green")
