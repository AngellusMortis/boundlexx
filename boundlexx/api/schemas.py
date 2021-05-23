import re
import warnings

from django.conf import settings
from rest_framework.exceptions import APIException
from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator

from boundlexx.api.common.serializers import AzureImageField


class DescriptiveAutoSchema(AutoSchema):
    def get_tags(self, path, method):
        tags = super().get_tags(path, method)

        for index, tag in enumerate(tags):
            tags[index] = tag.title()

        return tags

    def get_response_serializer(self, path, method):
        view = self.view

        if not hasattr(view, "get_response_serializer"):
            return self.get_serializer(path, method)

        try:
            return view.get_response_serializer()
        except APIException:
            warnings.warn(
                "{}.get_response_serializer() raised an exception during "
                "schema generation. Serializer fields will not be "
                "generated for {} {}.".format(view.__class__.__name__, method, path)
            )
        return None

    def get_responses(self, path, method):
        responses = super().get_responses(path, method)

        if not hasattr(self.view, "action"):
            return responses
        action = getattr(self.view, self.view.action)

        if hasattr(action, "example"):
            responses[list(responses.keys())[0]]["content"]["application/json"][
                "examples"
            ] = action.example

        if hasattr(action, "requires_processing") and action.requires_processing:
            responses = {"202": list(responses.values())[0]}

        return responses

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)

        if not hasattr(self.view, "action"):
            return operation

        action = getattr(self.view, self.view.action)
        if hasattr(action, "operation_id"):
            operation_id = action.operation_id
        else:
            base = self.view.basename or ""

            operation_id = (
                f"{self.view.action.lower()}" f"{base.title().replace('-', '')}"
            )
            if self.view.action.lower() == "list":
                operation_id += "s"
        summary = re.sub(r"(?<!^)(?=[A-Z])", " ", operation_id).title()

        operation["summary"] = summary
        operation["operationId"] = operation_id

        if hasattr(action, "deprecated"):
            operation["deprecated"] = action.deprecated

        return operation

    def _get_path_parameters(self, path, method):
        params = super()._get_path_parameters(path, method)

        if getattr(self.view, "is_timeseries", False):
            for param in params:
                lookup_field = self.view.lookup_field
                if lookup_field == "pk":
                    lookup_field = "id"
                if param["name"] == lookup_field:
                    param["description"] += " Pass `latest` to get newest item."
                    param["schema"] = {
                        "type": "string",
                        "pattern": r"^(\d+|latest)$",
                    }

        return params

    def map_field(self, field):
        if isinstance(field, AzureImageField):
            return {"type": "string", "format": "uri"}

        return super().map_field(field)


class BoundlexxSchemaGenerator(SchemaGenerator):
    def get_info(self, request=None):  # pylint: disable=arguments-differ
        # Title and version are required by openapi specification 3.x
        info = {
            "title": self.title or "",
            "version": getattr(request, "version", self.version) or "",
        }

        if self.description is not None:
            info["description"] = self.description

        return info

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request=request, public=public)

        schema["info"] = self.get_info(request)
        schema["servers"] = [
            {
                "url": f"https://api.boundlexx.app/api/{request.version}",
                "description": "Live Universe",
            },
            {
                "url": f"https://testing.boundlexx.app/api/{request.version}",
                "description": "Testing Universe",
            },
        ]

        if settings.DEBUG:
            schema["servers"].append(
                {
                    "url": f"https://local-boundlexx.wl.mort.is/api/{request.version}",
                    "description": "Local Instance",
                },
            )

        return schema
