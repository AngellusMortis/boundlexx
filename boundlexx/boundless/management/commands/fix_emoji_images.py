import djclick as click
from azure.common import AzureMissingResourceHttpError
from requests.exceptions import HTTPError

from boundlexx.api.tasks import purge_static_cache
from boundlexx.boundless.models import Emoji
from boundlexx.utils import download_image, get_django_image_from_file, make_thumbnail


@click.command()
def command():
    click.echo("Adding thumbs/renmaing images...")
    duplicates = []
    emojis = Emoji.objects.filter(image__isnull=False)
    with click.progressbar(
        emojis.iterator(), show_percent=True, show_pos=True, length=emojis.count()
    ) as pbar:
        for emoji in pbar:
            if emoji.image is not None and emoji.image.name:
                expected_name = f"{emoji.name}.png"
                if emoji.image.name != expected_name:
                    try:
                        temp_file = download_image(emoji.image.url)
                    except (AzureMissingResourceHttpError, HTTPError):
                        emoji.image = None
                        emoji.save()
                        continue
                    else:
                        emoji.image.delete()
                        emoji.image = get_django_image_from_file(
                            temp_file.name, expected_name
                        )
                    emoji.save()
                    emoji.refresh_from_db()

                    if emoji.image.name != expected_name:
                        duplicates.append(emoji.image.name)
                        continue

                if emoji.image_small is None or not emoji.image_small.name:
                    try:
                        emoji.image_small = make_thumbnail(emoji.image)
                    except AzureMissingResourceHttpError:
                        emoji.image = None

                expected_thumb_name = f"{emoji.name}_small.png"
                if emoji.image_small.name != expected_thumb_name:
                    try:
                        temp_file = download_image(emoji.image_small.url)
                    except (AzureMissingResourceHttpError, HTTPError):
                        emoji.image_small = None
                        emoji.save()
                        continue
                    else:
                        emoji.image_small.delete()
                        emoji.image_small = get_django_image_from_file(
                            temp_file.name, expected_thumb_name
                        )
                emoji.save()
                emoji.refresh_from_db()

                if emoji.image_small.name != expected_thumb_name:
                    duplicates.append(emoji.image_small.name)
                    continue

    click.echo("-----duplicates")
    click.echo(duplicates)

    click.echo("Purging CDN cache...")
    purge_static_cache(["emoji"])
