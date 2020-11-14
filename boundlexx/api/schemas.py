import re

from django.conf import settings
from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator


class DescriptiveAutoSchema(AutoSchema):
    def get_tags(self, path, method):
        tags = super().get_tags(path, method)

        for index, tag in enumerate(tags):
            tags[index] = tag.title()

        return tags

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

        if hasattr(action, "example"):
            operation["responses"]["200"]["content"]["application/json"][
                "examples"
            ] = action.example

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
