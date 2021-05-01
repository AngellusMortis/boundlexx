from datetime import timedelta

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import ProgrammingError
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from openpyxl.utils import get_column_letter

from boundlexx.api.models import ExportedFile

PURGE_CACHE_LOCK = "boundless:purge_cache_lock"
PURGE_CACHE_PATHS = "boundless:purge_cache_paths"
PURGE_CACHE_TASK = "boundlexx.api.tasks.purge_cache"
PURGE_GROUPS = {
    "__all__": ["/api/v1/*", "/api/v2/*"],
    "World": ["/api/v1/worlds/", "/api/v1/worlds/{world_id}/*"],
    "Color": ["/api/v1/colors/", "/api/v1/colors/{color_id}/*"],
    "Item": ["/api/v1/items/", "/api/v1/items/{item_id}/*"],
    "ItemRequestBasketPrice": [
        "/api/v1/items/{item_id}/request-baskets/*",
        "/api/v1/worlds/{world_id}/request-baskets/*",
    ],
    "ItemShopStandPrice": [
        "/api/v1/items/{item_id}/shop-stands/*",
        "/api/v1/worlds/{world_id}/shop-stands/*",
    ],
    "WorldPoll": [
        "/api/v1/worlds/{world_id}/polls/*",
    ],
    "ResourceCount": [
        "/api/v1/items/{item_id}/resource-counts/*",
        "/api/v1/items/{item_id}/resource-timeseries/*",
    ],
    "WorldBlockColor": [
        "/api/v1/colors/{color_id}/blocks/*",
        "/api/v1/items/{item_id}/colors/*",
        "/api/v1/worlds/{world_id}/block-colors/*",
    ],
}


def get_list_example(example_item):
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [example_item],
    }


def get_base_url(admin=False):
    try:
        site = Site.objects.get_current()
    except ProgrammingError:
        domain = "example.com"
    else:
        domain = site.domain

    if admin:
        domain = settings.ADMIN_DOMAIN_REPLACEMENTS.get(domain, domain)

    return f"{settings.API_PROTOCOL}://{domain}"


def queue_purge_paths(new_paths):
    schedule_task = False

    if not settings.AZURE_CDN_DYNAMIC_PURGE:
        return

    with cache.lock(PURGE_CACHE_LOCK, expire=10, auto_renewal=False):
        paths = cache.get(PURGE_CACHE_PATHS)

        if paths is None:
            paths = set()
        if len(paths) == 0:
            schedule_task = True

        paths.update(new_paths)

        cache.set(PURGE_CACHE_PATHS, paths, timeout=30)

    if schedule_task:
        run_time = timezone.now() + timedelta(seconds=15)
        task = PeriodicTask.objects.filter(task=PURGE_CACHE_TASK).first()

        if task is None:
            interval, _ = IntervalSchedule.objects.get_or_create(
                every=1, period=IntervalSchedule.SECONDS
            )

            task = PeriodicTask.objects.create(
                task=PURGE_CACHE_TASK,
                name="Purge Cache",
                interval=interval,
                one_off=True,
                start_time=run_time,
                enabled=True,
            )
        else:
            task.one_off = True
            task.start_time = run_time
            task.enabled = True
            task.save()


def set_column_widths(sheet):
    column_widths: list[int] = []
    for row in sheet.rows:
        for i, cell in enumerate(row):
            value = str(cell.value) if cell.value is not None else ""

            if len(column_widths) > i:
                if len(value) > column_widths[i]:
                    column_widths[i] = len(value)
            else:
                column_widths += [len(value)]

    for i, column_width in enumerate(column_widths):
        sheet.column_dimensions[get_column_letter(i + 1)].width = column_width + 2


def create_export_file(name, ext, description, content):
    xlsx_file = ContentFile(content)
    xlsx_file.name = f"{name}.{ext}"

    existing_file = ExportedFile.objects.filter(name=name).first()
    if existing_file is not None:
        existing_file.exported_file.delete()
        existing_file.delete()

    ExportedFile.objects.create(
        name=name, description=description, exported_file=xlsx_file
    )
