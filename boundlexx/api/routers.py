from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework_extensions.routers import ExtendedSimpleRouter

from boundlexx.api.schemas import BoundlexxSchemaGenerator


class APIDocsRouter(ExtendedSimpleRouter):
    def get_urls(self):
        urls = super().get_urls()

        schema_view = get_schema_view(
            title="Boundlexx",
            description=(
                "Boundless Lexicon API. Everything about the game Boundless"
            ),
            urlconf="boundlexx.api.urls",
            patterns=urls,
            generator_class=BoundlexxSchemaGenerator,
        )

        urls = [
            path(
                "",
                TemplateView.as_view(template_name="boundlexx/api/docs.html"),
                name="api-docs",
            ),
            path("schema/", schema_view, name="api-schema"),
        ] + urls

        return urls
