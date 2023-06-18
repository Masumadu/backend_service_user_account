import pytest

from app.models import RoleModel, UserRoleModel
from tests.base_test_case import BaseTestCase


class TestRoleModel(BaseTestCase):
    @pytest.mark.model
    def test_role_model(self, test_app):
        result = self.db_instance.query(RoleModel).get(self.role_model.id)
        assert result
        assert hasattr(result, "id")
        assert hasattr(result, "name")
        assert hasattr(result, "description")
        assert hasattr(result, "is_active")
        assert hasattr(result, "created_by")
        assert hasattr(result, "updated_by")
        assert hasattr(result, "deleted_by")
        assert hasattr(result, "created_at")
        assert hasattr(result, "updated_at")
        assert hasattr(result, "deleted_at")
        assert hasattr(result, "user_role")
        assert hasattr(result, "role_permission")

    def test_user_role_model(self, test_app):
        result = self.db_instance.query(UserRoleModel).get(self.user_role_model.id)
        assert result
        assert hasattr(result, "id")
        assert hasattr(result, "user_id")
        assert hasattr(result, "role_id")
        assert hasattr(result, "created_by")
        assert hasattr(result, "updated_by")
        assert hasattr(result, "deleted_by")
        assert hasattr(result, "created_at")
        assert hasattr(result, "updated_at")
        assert hasattr(result, "deleted_at")
        assert hasattr(result, "role")
