import pytest

from app.models import PermissionModel, ResourceModel
from tests.base_test_case import BaseTestCase


class TestResourceModel(BaseTestCase):
    @pytest.mark.model
    def test_resource_model(self, test_app):
        result = self.db_instance.query(ResourceModel).get(self.resource_model.id)
        assert result
        assert hasattr(result, "id")
        assert hasattr(result, "type")
        assert hasattr(result, "description")
        assert hasattr(result, "created_by")
        assert hasattr(result, "updated_by")
        assert hasattr(result, "deleted_by")
        assert hasattr(result, "created_at")
        assert hasattr(result, "updated_at")
        assert hasattr(result, "deleted_at")
        assert hasattr(result, "permissions")

    def test_permission_model(self, test_app):
        result = self.db_instance.query(PermissionModel).get(self.permission_model.id)
        assert result
        assert hasattr(result, "id")
        assert hasattr(result, "resource_id")
        assert hasattr(result, "mode")
        assert hasattr(result, "description")
        assert hasattr(result, "is_active")
        assert hasattr(result, "updated_by")
        assert hasattr(result, "deleted_by")
        assert hasattr(result, "created_at")
        assert hasattr(result, "updated_at")
        assert hasattr(result, "deleted_at")
        assert hasattr(result, "role_permission")
