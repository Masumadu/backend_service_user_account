import uuid

import pytest
from fastapi_pagination import Page

from app.core.exceptions import AppException
from app.enums import SortResultEnum
from app.models import PermissionModel, RoleModel
from app.utils import Params
from tests.base_test_case import BaseTestCase


class TestRoleController(BaseTestCase):
    @pytest.mark.controller
    def test_view_all_roles(self, test_app, caplog):
        result = self.role_controller.view_all_roles(
            sort_in=SortResultEnum.asc, paginate=Params()
        )

        assert result
        assert isinstance(result, Page)
        assert isinstance(result.items, list)

    @pytest.mark.controller
    def test_view_role(self, test_app, caplog):
        result = self.role_controller.view_role(obj_id=self.role_model.id)

        assert result
        assert isinstance(result, RoleModel)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.role_controller.view_role(obj_id=uuid.uuid4())
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_add_role(self, test_app):
        result = self.role_controller.add_role(
            auth_user=self.mock_decode_token(username=self.user_model.username),
            obj_data=self.role_test_data.create_role,
        )

        assert result
        assert isinstance(result, RoleModel)
        assert self.db_instance.query(RoleModel).count() == 2

    @pytest.mark.controller
    def test_assign_role_to_user(self, test_app):
        new_role = self.role_controller.add_role(
            auth_user=self.mock_decode_token(username=self.user_model.username),
            obj_data=self.role_test_data.create_role,
        )
        data = self.role_test_data.existing_user_role
        data["role_id"] = new_role.id
        result = self.role_controller.assign_role_to_user(
            auth_user=self.mock_decode_token(username=self.user_model.username),
            obj_data=data,
        )
        assert result
        assert isinstance(result, RoleModel)
        with pytest.raises(AppException.OperationErrorException) as op_exc:
            data["role_id"] = uuid.uuid4()
            self.role_controller.assign_role_to_user(
                auth_user=self.mock_decode_token(username=self.user_model.username),
                obj_data=data,
            )
        assert op_exc.value.status_code == 400

    @pytest.mark.controller
    def test_assign_permission_to_role(self, test_app):
        data = self.role_test_data.assign_permission_to_role
        data["permission_id"] = self.permission_model.id
        result = self.role_controller.assign_permission_to_role(
            auth_user=self.mock_decode_token(username=self.user_model.username),
            obj_data=data,
        )
        assert result
        assert isinstance(result, PermissionModel)
        with pytest.raises(AppException.OperationErrorException) as op_exc:
            data["permission_id"] = uuid.uuid4()
            self.role_controller.assign_permission_to_role(
                auth_user=self.mock_decode_token(username=self.user_model.username),
                obj_data=data,
            )
        assert op_exc.value.status_code == 400
