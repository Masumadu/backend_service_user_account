import os

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app import constants
from app.controllers import UserController
from app.core.database import Base, db, engine
from app.models import UserModel, UserOtpModel
from app.repositories import UserOtpRepository, UserRepository
from tests.data import UserTestData
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

    def setup_test_data(self):
        Base.metadata.create_all(bind=engine)
        self.user_test_data = UserTestData()
        self.user_model = UserModel(**self.user_test_data.existing_user)
        self.user_otp_model = UserOtpModel(**self.user_test_data.existing_otp)
        self.db_instance.add(self.user_model)
        self.db_instance.add(self.user_otp_model)
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

    def setup_patches(self, mocker, **kwargs):
        self.redis = mocker.patch(
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
