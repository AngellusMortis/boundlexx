from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework_extensions.routers import ExtendedSimpleRouter

from boundlexx.api.common.views import ForumFormatAPIView
from boundlexx.api.schemas import BoundlexxSchemaGenerator


class APIDocsRouter(ExtendedSimpleRouter):
    description: str = ""
    version: str = "v1"

    def __init__(self, description, version, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = description
        self.version = version

    def get_urls(self):
        urls = super().get_urls()

        schema_view = get_schema_view(
            title="Boundlexx",
            description=self.description,
            urlconf="boundlexx.api.urls",
            patterns=urls,
            generator_class=BoundlexxSchemaGenerator,
        )

        instance = self

        class DocsView(TemplateView):
            template_name = "boundlexx/api/docs.html"

            def get_context_data(self, **kwargs):
                return {
                    "url": f"{instance.version}:api-schema",
                    "version": instance.version,
                }

        if not settings.DEBUG:
            schema_view = cache_page(86400)(schema_view)

        urls = [
            path("", DocsView.as_view(), name="api-docs"),
            path("forum/", ForumFormatAPIView.as_view(), name="forum-format"),
            path("schema/", schema_view, name="api-schema"),
        ] + urls

        return urls
