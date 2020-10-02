from django.conf import settings
from pydiscourse import DiscourseClient


def get_forum_client():
    return DiscourseClient(
        settings.BOUNDLESS_FORUM_BASE_URL,
        api_username=settings.BOUNDLESS_FORUM_POST_USER,
        api_key=settings.BOUNDLESS_FORUM_POST_KEY,
    )
