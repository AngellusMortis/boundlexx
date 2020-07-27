from django.conf import settings


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """

    return settings.DEBUG and (
        request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS
        or request.META.get("HTTP_X_REAL_IP") in settings.INTERNAL_IPS
    )
