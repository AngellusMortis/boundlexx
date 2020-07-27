from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.static import serve
from django.views.generic import TemplateView

from boundlexx.api.urls import schema_view

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("admin_tools/", include("admin_tools.urls")),
    path(f"{settings.API_BASE}auth/", include("rest_framework.urls")),
    path(f"{settings.API_BASE}schema/", schema_view, name="openapi_schema"),
    path(settings.API_BASE, include("boundlexx.api.urls")),
    path("", TemplateView.as_view(template_name="boundlexx/api/docs.html")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls))
        ] + urlpatterns

elif settings.SERVE_STATIC_FILES_DEV:
    urlpatterns += [
        re_path(
            r"^static/(?P<path>.*)$",
            serve,
            {"document_root": settings.STATIC_ROOT},
        ),
    ]
