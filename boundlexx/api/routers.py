from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework_extensions.routers import ExtendedSimpleRouter

from boundlexx.api.common.views import ForumFormatAPIView
from boundlexx.api.schemas import BoundlexxSchemaGenerator

API_DESCRIPTION = """
Boundless Lexicon API. Everything about the game Boundless

This API is designed to be _relatively_ user friendly so you can always go to
any API URL and you should get a nice browsable API view for the endpoint. It
is also designed to give as much information as possible upfront and force you
to filter it down to just the information you need/want. As such every endpoint
has various filters avaiable to make use of if too much data is coming back for
you.

The API provides a nice "browsable API" view for each endpoint that allows you
to interact with the endpoint. It will show you all of the avaiable filters,
formats, etc. Because the API is kind of heavily cached by a CDN, this **format
is _not_ the default**. If you would like to use it, simply add `?format=api`
to the end of any endpoint to get it.

The API is also designed to give you as much data as avaiable, so you might
be getting more then you need. It is expected you use filters to trim down the
response content to only what you want back. The browsable API has all the
possible filters for each endpoint as does this OpenAPI spec. The OpenAPI spec
may extra filters that do not work on specific endpoints as there is a bit of
drift between the generation of the API vs. the generation of the docs that
have not been resolved yet (Sorry!).
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
            path("forum/", ForumFormatAPIView.as_view(), name="forum-format"),
            path("schema/", cache_page(86400)(schema_view), name="api-schema"),
        ] + urls

        return urls
