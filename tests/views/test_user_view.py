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

    @pytest.mark.view
    @mock.patch("app.services.keycloak_service.KeycloakAuthService.get_token")
    def test_user_login(self, mock_get_token, test_app):
        mock_get_token.return_value = self.mock_auth_service.get_token()
        response = test_app.post(
            f"{user_base_url}/token/access", json=self.user_test_data.login_user
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_user_profile(self, test_app):
        response = test_app.get(f"{user_base_url}/account/profile", headers=self.headers)
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    @pytest.mark.view
    @mock.patch("app.services.keycloak_service.KeycloakAuthService.refresh_token")
    def test_refresh_token(self, mock_refresh_token, test_app):
        mock_refresh_token.return_value = self.mock_auth_service.get_token()
        response = test_app.post(
            f"{user_base_url}/token/refresh",
            json={
                "user_id": str(self.user_model.id),
                "refresh_token": self.refresh_token,
            },
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_verify_phone(self, test_app):
        response = test_app.post(
            f"{user_base_url}/update/phone/verify",
            json={"new_phone": self.user_test_data.create_user.get("phone")},
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)

    @pytest.mark.view
    @mock.patch("app.services.keycloak_service.KeycloakAuthService.update_user")
    def test_change_phone(self, mock_update_user, test_app):
        mock_update_user.return_value = self.mock_auth_service.update_user()
        verify_phone = test_app.post(
            f"{user_base_url}/update/phone/verify",
            json={"new_phone": self.user_test_data.create_user.get("phone")},
            headers=self.headers,
        )
        confirm_otp = test_app.post(
            f"{user_base_url}/otp/confirm",
            json={
                "user_id": verify_phone.json().get("user_id"),
                "otp_code": self.user_otp_model.otp_code,
            },
        )
        response = test_app.post(
            f"{user_base_url}/update/phone",
            json={
                "new_phone": self.user_test_data.create_user.get("phone"),
                "sec_token": confirm_otp.json().get("sec_token"),
            },
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert self.user_test_data.existing_user.get("phone") != self.user_model.phone

    @pytest.mark.view
    @mock.patch("app.services.keycloak_service.KeycloakAuthService.change_password")
    def test_change_password(self, mock_change_password, test_app):
        mock_change_password.return_value = self.mock_auth_service.change_password()
        send_otp = test_app.post(
            f"{user_base_url}/otp/send",
            json={"user_id": str(self.user_model.id)},
            params={"sms": True},
        )
        confirm_otp = test_app.post(
            f"{user_base_url}/otp/confirm",
            json={
                "user_id": send_otp.json().get("user_id"),
                "otp_code": self.user_otp_model.otp_code,
            },
        )
        response = test_app.post(
            f"{user_base_url}/update/password",
            json={
                "old_password": self.user_test_data.existing_user.get("hash_password"),
                "new_password": self.user_test_data.create_user.get("password"),
                "sec_token": confirm_otp.json().get("sec_token"),
            },
            headers=self.headers,
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert (
            self.user_model.verify_password(
                self.user_test_data.existing_user.get("hash_password")
            )
            is False
        )

    @pytest.mark.view
    @mock.patch("app.services.keycloak_service.KeycloakAuthService.change_password")
    def test_reset_password(self, mock_change_password, test_app):
        mock_change_password.return_value = self.mock_auth_service.change_password()
        send_otp = test_app.post(
            f"{user_base_url}/otp/send",
            json={"phone": self.user_model.phone},
            params={"email": True},
        )
        confirm_otp = test_app.post(
            f"{user_base_url}/otp/confirm",
            json={
                "user_id": send_otp.json().get("user_id"),
                "otp_code": self.user_otp_model.otp_code,
            },
        )
        response = test_app.post(
            f"{user_base_url}/update/password/reset",
            json={
                "user_id": confirm_otp.json().get("user_id"),
                "new_password": self.user_test_data.create_user.get("password"),
                "sec_token": confirm_otp.json().get("sec_token"),
            },
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert (
            self.user_model.verify_password(
                self.user_test_data.existing_user.get("hash_password")
            )
            is False
        )

    @pytest.mark.view
    def test_send_otp(self, test_app):
        assert self.user_otp_model.otp_code is None
        assert self.user_otp_model.otp_code_expiration is None
        response = test_app.post(
            f"{user_base_url}/otp/send",
            json={"phone": self.user_model.phone},
            params={"email": True},
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert self.user_otp_model.otp_code is not None
        assert self.user_otp_model.otp_code_expiration is not None

    @pytest.mark.view
    def test_confirm_otp(self, test_app):
        send_otp = test_app.post(
            f"{user_base_url}/otp/send",
            json={"phone": self.user_model.phone},
            params={"email": True},
        )
        assert self.user_otp_model.sec_token is None
        assert self.user_otp_model.sec_token_expiration is None
        response = test_app.post(
            f"{user_base_url}/otp/confirm",
            json={
                "user_id": send_otp.json().get("user_id"),
                "otp_code": self.user_otp_model.otp_code,
            },
        )
        response_data = response.json()
        assert response_data
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert self.user_otp_model.otp_code is None
        assert self.user_otp_model.otp_code_expiration is None
        assert self.user_otp_model.sec_token is not None
        assert self.user_otp_model.sec_token_expiration is not None
