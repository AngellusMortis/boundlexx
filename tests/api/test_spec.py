import json

import yaml
from django.test import TestCase
from django.urls import reverse
from openapi_spec_validator import validate_spec


class TestUserCreationForm(TestCase):
    def test_validate_spec_json(self):
        schema_path = reverse("v1:api-schema")
        response = self.client.get(f"{schema_path}?format=openapi-json")

        spec_dict = json.loads(response.content.decode("utf8"))

        validation_response = validate_spec(spec_dict)
        print(validation_response)
        self.assertIsNone(validation_response)

    def test_validate_spec_equal(self):
        schema_path = reverse("v1:api-schema")
        response = self.client.get(f"{schema_path}?format=openapi-json")

        spec_dict_json = json.loads(response.content.decode(response.charset))

        response = self.client.get(f"{schema_path}?format=openapi")

        spec_dict_yaml = yaml.safe_load(response.content.decode("utf8"))

        self.assertEqual(spec_dict_json, spec_dict_yaml)
