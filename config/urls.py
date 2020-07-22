from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from bge.api.urls import schema_view

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("admin_tools/", include("admin_tools.urls")),
    path("accounts/", include("allauth.urls")),
    path("users/", include("bge.users.urls", namespace="users")),
    path("openid/", include("oidc_provider.urls", namespace="oidc_provider")),
    path("api/auth/", include("rest_framework.urls")),
    path("api/schema/", schema_view, name="openapi_schema"),
    path("api/docs/", TemplateView.as_view(template_name="bge/api/docs.html")),
    path("api/", include("bge.api.urls")),
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
