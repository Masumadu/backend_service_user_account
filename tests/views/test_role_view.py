import pytest

from app.api.api_v1.endpoints import role_base_url
from tests.base_test_case import BaseTestCase


class TestRoleView(BaseTestCase):
    @pytest.mark.view
    def test_get_all_roles(self, test_app):
        response = test_app.get(f"{role_base_url}/", headers=self.headers)
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    def test_get_role(self, test_app):
        response = test_app.get(
            f"{role_base_url}/{self.role_model.id}", headers=self.headers
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_add_role(self, test_app):
        response = test_app.post(
            f"{role_base_url}/",
            json=self.role_test_data.create_role,
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 201
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_assign_role_to_user(self, test_app):
        new_role = test_app.post(
            f"{role_base_url}/",
            json=self.role_test_data.create_role,
            headers=self.headers,
        )
        data = self.role_test_data.assign_role_to_user
        data["role_id"] = new_role.json().get("id")
        response = test_app.post(
            f"{role_base_url}/users",
            json=data,
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_assign_permission_to_role(self, test_app):
        response = test_app.post(
            f"{role_base_url}/permissions",
            json={
                "permission_id": str(self.permission_model.id),
                **self.role_test_data.assign_permission_to_role,
            },
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)
