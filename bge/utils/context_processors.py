from django.conf import settings
from django.http.request import HttpRequest


def settings_context(_request: HttpRequest):
    return {"settings": settings}
