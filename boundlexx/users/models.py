from django.contrib.auth.models import AbstractUser
from django.db.models import CharField


class User(AbstractUser):
    boundless_account_uid = CharField(max_length=128, null=True, blank=True)


# User.admin_app_label = "auth"  # type: ignore
