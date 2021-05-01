from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django_prometheus.models import ExportModelOperationsMixin


class User(ExportModelOperationsMixin("user"), AbstractUser):  # type: ignore
    boundless_account_uid = CharField(max_length=128, null=True, blank=True)
