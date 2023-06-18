import uuid

import pytest
from fastapi_pagination import Page

from app.core.exceptions import AppException
from app.enums import SortResultEnum
from app.models import PermissionModel, ResourceModel, RoleModel
from app.utils import Params
from tests.base_test_case import BaseTestCase


class TestResourceController(BaseTestCase):
    @pytest.mark.controller
    def test_view_all_resources(self, test_app, caplog):
        result = self.resource_controller.view_all_resource(
            sort_in=SortResultEnum.asc, paginate=Params()
        )

        assert result
        assert isinstance(result, Page)
        assert isinstance(result.items, list)

    @pytest.mark.controller
    def test_view_resource(self, test_app, caplog):
        result = self.resource_controller.view_resource(obj_id=self.resource_model.id)

        assert result
        assert isinstance(result, ResourceModel)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.resource_controller.view_resource(obj_id=uuid.uuid4())
        assert not_found.value.status_code == 404
        assert "not found" in not_found.value.error_message

    @pytest.mark.controller
    def test_assign_permission_to_resource(self, test_app):
        new_resource = self.resource_controller.add_resource(
            auth_user=self.mock_decode_token(username=self.user_model.username),
            obj_data=self.resource_test_data.create_resource,
        )
        data = self.resource_test_data.assign_permission_to_resource
        data["resource_id"] = new_resource.id
        result = self.resource_controller.assign_permission_to_resource(
            auth_user=self.mock_decode_token(username=self.user_model.username),
            obj_data=data,
        )

        assert result
        assert isinstance(result, PermissionModel)
        assert self.db_instance.query(PermissionModel).count() == 2

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
