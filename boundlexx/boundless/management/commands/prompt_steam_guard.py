import os
from shutil import copy2

import djclick as click
from django.conf import settings
from steam.client import SteamClient


@click.command()
def command():
    client = SteamClient()
    client.set_credential_location(settings.STEAM_SENTRY_DIR)

    click.echo("Logging into Steam...")
    client.cli_login(
        username=settings.STEAM_USERNAME, password=settings.STEAM_PASSWORD
    )

    # copy to correct location for `auth-ticket.js`
    src = os.path.join(
        settings.STEAM_SENTRY_DIR, f"{settings.STEAM_USERNAME}_sentry.bin"
    )
    dest = os.path.join(
        settings.STEAM_SENTRY_DIR, f"sentry.{settings.STEAM_USERNAME}.bin"
    )
    copy2(src, dest)

    click.echo("Login successful. Steam Guard should not prompt anymore")
    client.logout()
