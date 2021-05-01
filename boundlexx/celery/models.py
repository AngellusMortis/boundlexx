from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_results.models import TaskResult


class TaskOutput(models.Model):
    task = models.ForeignKey(TaskResult, on_delete=models.CASCADE)
    output = models.TextField(_("Task Output"))
