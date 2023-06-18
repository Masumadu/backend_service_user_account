import pytest

from app.api.api_v1.endpoints import resource_base_url
from tests.base_test_case import BaseTestCase


class TestResourceView(BaseTestCase):
    @pytest.mark.view
    def test_view_all_resources(self, test_app):
        response = test_app.get(f"{resource_base_url}/", headers=self.headers)
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    def test_get_role(self, test_app):
        response = test_app.get(
            f"{resource_base_url}/{self.resource_model.id}", headers=self.headers
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_add_resource(self, test_app):
        response = test_app.post(
            f"{resource_base_url}/",
            json=self.resource_test_data.create_resource,
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 201
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_assign_permission_to_resource(self, test_app):
        new_resource = test_app.post(
            f"{resource_base_url}/",
            json=self.resource_test_data.create_resource,
            headers=self.headers,
        )
        response = test_app.post(
            f"{resource_base_url}/permissions",
            json={
                "resource_id": new_resource.json().get("id"),
                **self.resource_test_data.assign_permission_to_resource,
            },
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)
