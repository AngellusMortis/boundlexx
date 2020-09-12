from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework_extensions.routers import ExtendedSimpleRouter

from boundlexx.api.schemas import BoundlexxSchemaGenerator

API_DESCRIPTION = """
Boundless Lexicon API. Everything about the game Boundless

This API is designed to be _relatively_ user friendly so you can always go to
any API URL and you should get a nice browsable API view for the endpoint. It
is also designed to give as much information as possible upfront and force you
to filter it down to just the information you need/want. As such every endpoint
has various filters avaiable to make use of if too much data is coming back for
you.

The API is some what heavily cached by a CDN, so you must be explicit when
you make requests for what format you want. Chances are, the browsable API
will always be returned by default. If you actually want JSON for your code,
you need to request it. You can add a `?format=` filter to any API URL to
force a specific format.

* `format=api` - will force the browsable API
* `format=json` - will force a JSON response
"""


class APIDocsRouter(ExtendedSimpleRouter):
    def get_urls(self):
        urls = super().get_urls()

        schema_view = get_schema_view(
            title="Boundlexx",
            description=API_DESCRIPTION,
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
