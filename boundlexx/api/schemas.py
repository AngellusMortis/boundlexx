from django.urls import reverse
from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator


class DescriptiveAutoSchema(AutoSchema):
    def __init__(self, *args, tags=None, **kwargs):
        self._tags = tags
        super().__init__(*args, **kwargs)

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)

        tags = [self.view.basename.title()]

        action = getattr(self.view, self.view.action)
        if hasattr(action, "operation_id"):
            operation_id = action.operation_id
        else:
            operation_id = f"{self.view.action}-{self.view.basename}".lower()
            operation_id = operation_id.replace("_", "-")
            if self.view.action.lower() == "list":
                operation_id += "s"
        summary = operation_id.title().replace("-", " ")

        operation["summary"] = summary
        operation["operationId"] = operation_id
        operation["tags"] = self._tags or tags

        if hasattr(action, "example"):
            operation["responses"]["200"]["content"]["application/json"][
                "examples"
            ] = action.example

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

        return schema
