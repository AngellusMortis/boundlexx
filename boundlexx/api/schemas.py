from rest_framework.schemas.openapi import AutoSchema


class DescriptiveAutoSchema(AutoSchema):
    def get_operation(self, path, method):
        operation = super().get_operation(path, method)

        tags = [self.view.basename.title()]
        operation_id = f"{self.view.action} {self.view.basename}".title()
        if self.view.action.lower() == "list":
            operation_id += "s"

        operation["operationId"] = operation_id
        operation["tags"] = operation.get("tags", []) + tags

        action = getattr(self.view, self.view.action)
        if hasattr(action, "example"):
            operation["responses"]["200"]["content"]["application/json"][
                "examples"
            ] = action.example

        return operation
