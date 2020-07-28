from django.urls import reverse
from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator


class DescriptiveAutoSchema(AutoSchema):
    def __init__(self, *args, tags=None, **kwargs):
        self._tags = tags
        super().__init__(*args, **kwargs)

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)

        tags = [self.view.basename.title()]
        operation_id = f"{self.view.action} {self.view.basename}"
        operation_id = operation_id.title().replace("-", " ")

        if self.view.action.lower() == "list":
            operation_id += "s"

        operation["operationId"] = operation_id
        operation["tags"] = self._tags or tags

        action = getattr(self.view, self.view.action)
        if hasattr(action, "example"):
            operation["responses"]["200"]["content"]["application/json"][
                "examples"
            ] = action.example

        return operation


class BoundlexxSchemaGenerator(SchemaGenerator):
    def get_info(self, request):  # pylint: disable=arguments-differ
        # Title and version are required by openapi specification 3.x
        info = {
            "title": self.title or "",
            "version": getattr(request, "version", ""),
        }

        if self.description is not None:
            info["description"] = self.description

        return info

    def get_paths(self, request=None):
        self.url = reverse(f"{request.version}:api-docs")

        return super().get_paths(request=request)

    def get_schema(self, request=None, public=False):
        """
        Generate a OpenAPI schema.
        """
        self._initialise_endpoints()

        paths = self.get_paths(request)
        if not paths:
            return None

        schema = {
            "openapi": "3.0.2",
            "info": self.get_info(request),
            "paths": paths,
        }

        return schema
