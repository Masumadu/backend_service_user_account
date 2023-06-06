from unittest import mock

import pytest

from app.api.api_v1.endpoints.user_view import user_base_url
from tests.base_test_case import BaseTestCase


class TestUserView(BaseTestCase):
    @pytest.mark.view
    def test_get_all_users(self, test_app):
        response = test_app.get(f"{user_base_url}/", headers=self.headers)
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    def test_get_user(self, test_app):
        response = test_app.get(
            f"{user_base_url}/{self.user_model.id}", headers=self.headers
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    @pytest.mark.view
    @mock.patch("app.services.keycloak_service.KeycloakAuthService.create_user")
    def test_create_user(self, mock_create_user, test_app):
        mock_create_user.return_value = self.mock_auth_service.create_user(
            obj_data=self.user_test_data.create_user
        )
        response = test_app.post(
            f"{user_base_url}/",
            json=self.user_test_data.create_user,
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 201
        assert isinstance(response_data, dict)

    @pytest.mark.view
    @mock.patch("app.services.keycloak_service.KeycloakAuthService.update_user")
    def test_update_user(self, mock_update_user, test_app):
        mock_update_user.return_value = self.mock_auth_service.update_user(
            obj_data=self.user_test_data.update_user
        )
        response = test_app.patch(
            f"{user_base_url}/{self.user_model.id}",
            json=self.user_test_data.update_user,
            headers=self.headers,
        )
        response_data = response.json()
        assert response.status_code == 200
        assert response_data
        assert isinstance(response_data, dict)

    @pytest.mark.view
    @mock.patch("app.services.keycloak_service.KeycloakAuthService.update_user")
    def test_delete_user(self, mock_delete_user, test_app):
        response = test_app.delete(
            f"{user_base_url}/{self.user_model.id}", headers=self.headers
        )
        assert response.status_code == 204
