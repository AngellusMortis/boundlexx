import os
import time
from shutil import copy2

import djclick as click
from django.conf import settings
from steam.client import SteamClient


@click.command()
def command():
    client = SteamClient()
    client.set_credential_location(settings.STEAM_SENTRY_DIR)

    for index, username in enumerate(settings.STEAM_USERNAMES):
        click.echo(f"Logging into Steam as {username}...")
        client.cli_login(username=username, password=settings.STEAM_PASSWORDS[index])

        time.sleep(5)

        # copy to correct location for `auth-ticket.js`
        src = os.path.join(settings.STEAM_SENTRY_DIR, f"{username}_sentry.bin")
        dest = os.path.join(settings.STEAM_SENTRY_DIR, f"sentry.{username}.bin")
        copy2(src, dest)

        click.echo("Login successful. Steam Guard should not prompt anymore")
        client.logout()
