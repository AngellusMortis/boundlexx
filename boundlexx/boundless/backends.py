import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from requests import HTTPError

from boundlexx.boundless.client import BoundlessClient

User = get_user_model()


class BoundlessAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        client = BoundlessClient()

        try:
            boundless_jwt = client.login_user(username, password)
        except HTTPError:
            return None

        boundless_user = jwt.decode(boundless_jwt, verify=False)

        try:
            user = User.objects.get(username=boundless_user["username"])
        except User.DoesNotExist:
            user = None  # type: ignore
            if settings.BOUNDLESS_AUTH_AUTO_CREATE:
                user = User.objects.create(username=boundless_user["username"])

        return user
