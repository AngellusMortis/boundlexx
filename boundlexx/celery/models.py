from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_results.models import TaskResult
from django_prometheus.models import ExportModelOperationsMixin


class TaskOutput(ExportModelOperationsMixin("task_output"), models.Model):  # type: ignore # noqa E501
    task = models.ForeignKey(TaskResult, on_delete=models.CASCADE)
    output = models.TextField(_("Task Output"))
