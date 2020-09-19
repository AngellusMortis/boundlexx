from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_celery_results.models import TaskResult

from .utils import get_output_for_task

try:
    ALLOW_EDITS = settings.DJANGO_CELERY_RESULTS["ALLOW_EDITS"]  # type: ignore
except (AttributeError, KeyError):
    ALLOW_EDITS = False

if admin.site.is_registered(TaskResult):
    admin.site.unregister(TaskResult)


@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    date_hierarchy = "date_done"
    list_display = (
        "task_id",
        "task_name",
        "date_created",
        "date_done",
        "status",
        "worker",
    )
    list_filter = ("status", "date_done", "task_name", "worker")
    readonly_fields = (
        "date_created",
        "date_done",
        "result",
        "meta",
        "task_output",
    )
    search_fields = ("task_name", "task_id", "status")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "task_id",
                    "task_name",
                    "status",
                    "worker",
                    "content_type",
                    "content_encoding",
                ),
                "classes": ("extrapretty", "wide"),
            },
        ),
        (
            _("Parameters"),
            {
                "fields": ("task_args", "task_kwargs"),
                "classes": ("extrapretty", "wide"),
            },
        ),
        (
            _("Result"),
            {
                "fields": (
                    "result",
                    "date_created",
                    "date_done",
                    "traceback",
                    "meta",
                    "task_output",
                ),
                "classes": ("extrapretty", "wide"),
            },
        ),
    )

    def task_output(self, instance):
        if not instance or not instance.pk:
            return None

        output_lines = get_output_for_task(instance)

        if len(output_lines) == 0:
            return None

        output = "\n".join(output_lines)
        return mark_safe(  # nosec
            f"<br><pre style='white-space: pre-wrap;'>{output}</pre>"
        )

    def get_readonly_fields(self, request, obj=None):
        if ALLOW_EDITS:
            return self.readonly_fields

        local_fields = list({field.name for field in self.opts.local_fields})
        return local_fields + ["task_output"]
