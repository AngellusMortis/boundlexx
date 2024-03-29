from io import BytesIO
from tempfile import NamedTemporaryFile

import environ
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
from pydiscourse import DiscourseClient

env = environ.Env()


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """

    return settings.DEBUG and (
        request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS
        or request.META.get("HTTP_X_REAL_IP") in settings.INTERNAL_IPS
    )


def make_thumbnail(image_file, size=50):
    img = Image.open(image_file)

    img.thumbnail((size, size), Image.LANCZOS)

    image_content = BytesIO()
    img.save(image_content, format="PNG")

    new_image = ContentFile(image_content.getvalue())
    new_image.name = image_file.name.replace(".png", "_small.png")

    return new_image


def download_image(image_url):
    tries = 4
    while tries >= 0:
        img_response = requests.get(image_url, timeout=5)
        try:
            img_response.raise_for_status()
        except requests.exceptions.HTTPError:
            if tries > 0:
                tries -= 1
            else:
                raise
        else:
            temp_file = NamedTemporaryFile(  # pylint: disable=consider-using-with
                "wb", delete=False
            )
            temp_file.write(img_response.content)
            temp_file.close()
            break

    return temp_file


def get_django_image(image, name):
    image_content = BytesIO()
    image.save(image_content, format="PNG")

    django_image = ContentFile(image_content.getvalue())
    django_image.name = name

    return django_image


def get_django_image_from_file(image_path, name):
    return get_django_image(Image.open(image_path), name)


def get_forum_client():
    return DiscourseClient(
        env("BOUNDLESS_FORUM_BASE_URL"),
        api_username=env("BOUNDLESS_FORUM_POST_USER"),
        api_key=env("BOUNDLESS_FORUM_POST_KEY"),
    )
