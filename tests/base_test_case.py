import os

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app import constants
from app.controllers import SampleController
from app.core.database import Base, db, engine
from app.models import SampleModel
from app.repositories import SampleRepository
from tests.data import SampleTestData
from tests.utils import MockSideEffects


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
        self.token_type = "access"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        Base.metadata.drop_all(bind=engine)
        test_client = TestClient(app)
        self.setup_test_data()
        self.setup_patches(mocker, token_type=self.token_type)
        self.instantiate_classes()
        yield test_client

    def setup_test_data(self):
        Base.metadata.create_all(bind=engine)
        self.sample_test_data = SampleTestData()
        self.sample_model = SampleModel(**self.sample_test_data.exiting_sample)
        self.db_instance.add(self.sample_model)
        self.db_instance.commit()

    def instantiate_classes(self):
        self.sample_repository = SampleRepository(redis_service=self.redis)
        self.sample_controller = SampleController(
            sample_repository=self.sample_repository
        )

    def setup_patches(self, mocker, **kwargs):
        self.redis = mocker.patch(
            "app.services.redis_service.redis_conn", fakeredis.FakeStrictRedis()
        )
        self.jwt_decode = mocker.patch(
            "app.utils.auth.jwt.decode",
            return_value=self.mock_decode_token(self.token_type),
        )
