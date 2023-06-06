import pytest

from app.models import UserModel, UserOtpModel
from tests.base_test_case import BaseTestCase


class TestUserModels(BaseTestCase):
    @pytest.mark.model
    def test_user_model(self, test_app):
        result = self.db_instance.query(UserModel).get(self.user_model.id)
        assert result
        assert hasattr(result, "id")
        assert hasattr(result, "first_name")
        assert hasattr(result, "last_name")
        assert hasattr(result, "username")
        assert hasattr(result, "email")
        assert hasattr(result, "phone")
        assert hasattr(result, "birth_date")
        assert hasattr(result, "national_id")
        assert hasattr(result, "id_expiration")
        assert hasattr(result, "password")
        assert hasattr(result, "is_verified")
        assert hasattr(result, "last_active")
        assert hasattr(result, "auth_provider_id")
        assert hasattr(result, "status")
        assert hasattr(result, "is_deleted")
        assert hasattr(result, "meta_data")
        assert hasattr(result, "created_at")
        assert hasattr(result, "deleted_at")
        assert result.id is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        assert result.deleted_at is None

    def test_user_otp_model(self, test_app):
        result = self.db_instance.query(UserOtpModel).get(self.user_otp_model.id)
        assert result
        assert hasattr(result, "id")
        assert hasattr(result, "user_id")
        assert hasattr(result, "otp_code")
        assert hasattr(result, "otp_code_expiration")
        assert hasattr(result, "sec_token")
        assert hasattr(result, "sec_token_expiration")
        assert hasattr(result, "created_by")
        assert hasattr(result, "updated_by")
        assert hasattr(result, "deleted_by")
        assert hasattr(result, "created_at")
        assert hasattr(result, "updated_at")
        assert hasattr(result, "deleted_at")
        assert result.id is not None
        assert result.otp_code is None
        assert result.otp_code_expiration is None
        assert result.sec_token is None
        assert result.sec_token_expiration is None
