from django.http import Http404
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.settings import api_settings


class IgnoreClientContentNegotiation(BaseContentNegotiation):
    settings = api_settings

    def select_parser(self, request, parsers):
        """
        Select the first parser in the `.parser_classes` list.
        """
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix=None):
        """
        Select the first renderer in the `.renderer_classes` list.
        """

        format_query_param = self.settings.URL_FORMAT_OVERRIDE
        format_name = format_suffix or request.query_params.get(format_query_param)

        if format_name:
            renderers = self.filter_renderers(renderers, format_name)

        return (renderers[0], renderers[0].media_type)

    def filter_renderers(self, renderers, format_name):
        """
        If there is a '.json' style format suffix, filter the renderers
        so that we only negotiation against those that accept that format.
        """
        renderers = [
            renderer for renderer in renderers if renderer.format == format_name
        ]
        if not renderers:
            raise Http404
        return renderers
