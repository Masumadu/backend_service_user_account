import os

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app import constants
from app.controllers import ResourceController, RoleController, UserController
from app.core.database import Base, db, engine
from app.models import (
    PermissionModel,
    ResourceModel,
    RoleModel,
    UserModel,
    UserOtpModel,
    UserRoleModel,
)
from app.repositories import (
    PermissionRepository,
    ResourceRepository,
    RolePermissionRepository,
    RoleRepository,
    UserOtpRepository,
    UserRepository,
    UserRoleRepository,
)
from tests.data import ResourceTestData, RoleTestData, UserTestData
from tests.utils import MockKeycloakAuthService, MockSideEffects


@pytest.mark.usefixtures("app")
class BaseTestCase(MockSideEffects):
    db_instance = db

    @pytest.fixture
    def test_app(self, app, mocker):
        config_env = os.getenv("FASTAPI_CONFIG")
        assert config_env == constants.TESTING_ENVIRONMENT, constants.ENV_ERROR.format(
            config_env
        )
        self.access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # noqa: E501
        self.refresh_token = self.access_token
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        Base.metadata.drop_all(bind=engine)
        test_client = TestClient(app)
        self.setup_test_data()
        self.setup_patches(mocker)
        self.instantiate_classes()
        try:
            yield test_client
        finally:
            self.db_instance.close()
            Base.metadata.drop_all(bind=engine)

    def setup_test_data(self):
        Base.metadata.create_all(bind=engine)
        self.user_test_data = UserTestData()
        self.user_model = UserModel(**self.user_test_data.existing_user)
        self.commit_data_model(self.user_model)
        self.user_otp_model = UserOtpModel(**self.user_test_data.existing_otp)
        self.commit_data_model(self.user_otp_model)
        self.role_test_data = RoleTestData()
        self.role_model = RoleModel(**self.role_test_data.existing_role)
        self.commit_data_model(self.role_model)
        self.user_role_model = UserRoleModel(**self.role_test_data.existing_user_role)
        self.commit_data_model(self.user_role_model)
        self.resource_test_data = ResourceTestData()
        self.resource_model = ResourceModel(**self.resource_test_data.existing_resource)
        self.commit_data_model(self.resource_model)
        self.permission_model = PermissionModel(
            **self.resource_test_data.existing_permission
        )
        self.commit_data_model(self.permission_model)

    def commit_data_model(self, model):
        self.db_instance.add(model)
        self.db_instance.commit()

    def instantiate_classes(self):
        self.user_repository = UserRepository()
        self.user_otp_repository = UserOtpRepository()
        self.mock_auth_service = MockKeycloakAuthService()
        self.user_controller = UserController(
            user_repository=self.user_repository,
            user_otp_repository=self.user_otp_repository,
            keycloak_auth_service=self.mock_auth_service,
        )
        self.role_repository = RoleRepository()
        self.user_role_repository = UserRoleRepository()
        self.permission_repository = PermissionRepository()
        self.role_permission_repository = RolePermissionRepository()
        self.role_controller = RoleController(
            role_repository=self.role_repository,
            user_repository=self.user_repository,
            user_role_repository=self.user_role_repository,
            permission_repository=self.permission_repository,
            role_permission_repository=self.role_permission_repository,
        )
        self.resource_repository = ResourceRepository()
        self.resource_controller = ResourceController(
            resource_repository=self.resource_repository,
            permission_repository=self.permission_repository,
        )

    def setup_patches(self, mocker, **kwargs):
        mocker.patch(
            "app.services.redis_service.redis_conn", fakeredis.FakeStrictRedis()
        )
        mocker.patch(
            "app.utils.auth.jwt.decode",
            return_value=self.mock_decode_token(self.user_model.username),
        )
        mocker.patch(
            "app.notifications.sms_notification_handler.publish_to_kafka",
            return_value=True,
        )
        mocker.patch(
            "app.notifications.email_notification_handler.publish_to_kafka",
            return_value=True,
        )
