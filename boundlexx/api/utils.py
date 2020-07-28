from django.conf import settings
from django.contrib.sites.models import Site
from django.db import ProgrammingError


def get_list_example(example_item):
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [example_item],
    }


def get_base_url():
    try:
        site = Site.objects.get_current()
    except ProgrammingError:
        domain = "example.com"
    else:
        domain = site.domain

    return f"{settings.API_PROTOCOL}://{domain}"
