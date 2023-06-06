import uuid
from datetime import datetime, timedelta
from time import sleep

import pytest
from fastapi_pagination import Page

from app.core.exceptions import AppException
from app.enums import SortResultEnum
from app.models import UserModel
from app.utils import Params
from tests.base_test_case import BaseTestCase


class TestUserController(BaseTestCase):
    @pytest.mark.controller
    def test_get_all_user(self, test_app, caplog):
        result = self.user_controller.get_all_users(
            sort_in=SortResultEnum.asc, paginate=Params()
        )

        assert result
        assert isinstance(result, Page)
        assert isinstance(result.items, list)

    @pytest.mark.controller
    def test_get_user(self, test_app, caplog):
        result = self.user_controller.get_user(obj_id=self.user_model.id)

        assert result
        assert isinstance(result, UserModel)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.get_user(obj_id=uuid.uuid4())
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_create_user(self, test_app):
        result = self.user_controller.create_user(
            obj_data=self.user_test_data.create_user
        )

        assert result
        assert isinstance(result, UserModel)
        assert self.db_instance.query(UserModel).count() == 2

    @pytest.mark.controller
    def test_update_user(self, test_app):
        result = self.user_controller.update_user(
            obj_id=self.user_model.id, obj_data=self.user_test_data.update_user
        )

        assert result
        assert isinstance(result, UserModel)
        assert result.email == self.user_test_data.update_user.get("email")
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.update_user(
                obj_id=uuid.uuid4(), obj_data=self.user_test_data.update_user
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_delete_user(self, test_app):
        result = self.user_controller.delete_user(obj_id=self.user_model.id)

        assert self.user_model.is_deleted is True
        assert self.user_model.deleted_at is not None
        assert result is None
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.delete_user(obj_id=uuid.uuid4())
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    def test_user_profile(self, test_app):
        result = self.user_controller.user_profile(
            auth_user=self.mock_decode_token(self.user_model.username)
        )

        assert result
        assert isinstance(result, UserModel)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.user_profile(
                auth_user=self.mock_decode_token(
                    username=self.user_test_data.create_user.get("username")
                )
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    def test_user_login(self, test_app):
        result = self.user_controller.user_login(obj_data=self.user_test_data.login_user)

        assert result
        assert isinstance(result, dict)
        with pytest.raises(AppException.BadRequestException) as bad_req_exc:
            self.user_controller.user_login(
                obj_data={
                    "username": self.user_test_data.create_user.get("username"),
                    "password": self.user_test_data.create_user.get("password"),
                }
            )
        assert bad_req_exc.value.status_code == 400
        assert "invalid" in bad_req_exc.value.error_message

    def test_refresh_user_token(self, test_app):
        result = self.user_controller.refresh_user_token(
            obj_data={"user_id": self.user_model.id, "refresh_token": self.refresh_token}
        )

        assert result
        assert isinstance(result, dict)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.refresh_user_token(
                obj_data={"user_id": uuid.uuid4(), "refresh_token": self.refresh_token}
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_verify_phone(self, test_app):
        result = self.user_controller.verify_phone(
            obj_data={"new_phone": self.user_test_data.create_user.get("phone")},
            auth_user=self.mock_decode_token(username=self.user_model.username),
        )
        assert result
        assert isinstance(result, dict)
        assert self.user_otp_model.otp_code is not None
        assert self.user_otp_model.otp_code_expiration is not None
        assert self.user_otp_model.sec_token is not None
        assert self.user_otp_model.sec_token_expiration is not None
        with pytest.raises(AppException.ResourceExistsException) as resource_exist_exc:
            self.user_controller.verify_phone(
                auth_user=self.mock_decode_token(username=self.user_model.username),
                obj_data={"new_phone": self.user_model.phone},
            )
        assert resource_exist_exc.value.status_code == 409
        assert "exist" in resource_exist_exc.value.error_message
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.verify_phone(
                auth_user=self.mock_decode_token(
                    username=self.user_test_data.create_user.get("username")
                ),
                obj_data={"new_phone": self.user_model.password},
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_change_phone(self, test_app):
        self.user_controller.verify_phone(
            auth_user=self.mock_decode_token(username=self.user_model.username),
            obj_data={"new_phone": self.user_test_data.create_user.get("phone")},
        )
        self.user_controller.confirm_otp_code(
            obj_data={"user_id": self.user_model.id, "otp_code": "123456"}
        )
        result = self.user_controller.change_phone(
            obj_data={
                "new_phone": self.user_test_data.create_user.get("phone"),
                "sec_token": self.user_otp_model.sec_token,
            },
            auth_user=self.mock_decode_token(username=self.user_model.username),
        )
        assert result
        assert isinstance(result, dict)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.change_phone(
                obj_data={
                    "new_phone": self.user_test_data.create_user.get("phone"),
                    "sec_token": self.user_otp_model.sec_token,
                },
                auth_user=self.mock_decode_token(
                    username=self.user_test_data.create_user.get("username")
                ),
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_change_user_password(self, test_app):
        self.user_controller.send_otp_code(
            sms=True,
            email=True,
            obj_data={"user_id": self.user_model.id},
        )
        self.user_controller.confirm_otp_code(
            obj_data={"user_id": self.user_model.id, "otp_code": "123456"}
        )
        result = self.user_controller.change_user_password(
            obj_data={
                "old_password": self.user_test_data.existing_user.get("hash_password"),
                "new_password": self.user_test_data.create_user.get("password"),
                "sec_token": self.user_otp_model.sec_token,
            },
            auth_user=self.mock_decode_token(username=self.user_model.username),
        )
        assert result
        assert isinstance(result, dict)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.change_phone(
                obj_data={
                    "old_password": self.user_test_data.existing_user.get(
                        "hash_password"
                    ),
                    "new_password": self.user_test_data.create_user.get("password"),
                    "sec_token": self.user_otp_model.sec_token,
                },
                auth_user=self.mock_decode_token(
                    username=self.user_test_data.create_user.get("username")
                ),
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_reset_user_password(self, test_app):
        self.user_controller.send_otp_code(
            sms=True,
            email=True,
            obj_data={"phone": self.user_model.phone},
        )
        self.user_controller.confirm_otp_code(
            obj_data={"user_id": self.user_model.id, "otp_code": "123456"}
        )
        result = self.user_controller.reset_user_password(
            obj_data={
                "user_id": self.user_model.id,
                "new_password": self.user_test_data.create_user.get("password"),
                "sec_token": self.user_otp_model.sec_token,
            }
        )
        assert result
        assert isinstance(result, dict)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.reset_user_password(
                obj_data={
                    "user_id": uuid.uuid4(),
                    "new_password": self.user_test_data.create_user.get("password"),
                    "sec_token": self.user_otp_model.sec_token,
                }
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_send_otp_code(self, test_app):
        result = self.user_controller.send_otp_code(
            sms=True,
            email=True,
            obj_data={"phone": self.user_model.phone},
        )
        assert result
        assert isinstance(result, dict)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.send_otp_code(
                sms=True,
                email=True,
                obj_data={"phone": self.user_test_data.create_user.get("phone")},
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message
        with pytest.raises(AppException.BadRequestException) as bad_req_exc:
            self.user_controller.send_otp_code(
                sms=None,
                email=None,
                obj_data={"phone": self.user_test_data.create_user.get("phone")},
            )
        assert bad_req_exc.value.status_code == 400
        assert "invalid" in bad_req_exc.value.error_message

    @pytest.mark.controller
    def test_confirm_otp_code(self, test_app):
        self.user_controller.send_otp_code(
            sms=True,
            email=True,
            obj_data={"phone": self.user_model.phone},
        )
        result = self.user_controller.confirm_otp_code(
            obj_data={
                "user_id": self.user_model.id,
                "otp_code": self.user_otp_model.otp_code,
            }
        )
        assert result
        assert isinstance(result, dict)
        with pytest.raises(AppException.InvalidTokenException) as invalid_token:
            self.user_controller.confirm_otp_code(
                obj_data={
                    "user_id": self.user_model.id,
                    "otp_code": self.user_otp_model.sec_token,
                }
            )
        assert invalid_token.value.status_code == 400
        assert "invalid" in invalid_token.value.error_message
        with pytest.raises(AppException.InvalidTokenException) as expired_token:
            self.user_otp_repository.update_by_id(
                obj_id=self.user_otp_model.id,
                obj_in={"otp_code_expiration": datetime.utcnow() + timedelta(seconds=1)},
            )
            sleep(1)
            self.user_controller.confirm_otp_code(
                obj_data={
                    "user_id": self.user_model.id,
                    "otp_code": self.user_otp_model.otp_code,
                }
            )
        assert expired_token.value.status_code == 400
        assert "expired" in expired_token.value.error_message
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.user_controller.confirm_otp_code(
                obj_data={
                    "user_id": self.user_otp_model.id,
                    "otp_code": self.user_otp_model.otp_code,
                }
            )
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message
