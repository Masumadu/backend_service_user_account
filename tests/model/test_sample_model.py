import pytest

from app.models import SampleModel
from tests.base_test_case import BaseTestCase


class TestSampleModels(BaseTestCase):
    @pytest.mark.model
    def test_sample_model(self, test_app):
        result = self.db_instance.query(SampleModel).get(self.sample_model.id)
        assert result
        assert hasattr(result, "id")
        assert hasattr(result, "name")
        assert hasattr(result, "country")
        assert hasattr(result, "agent")
        assert hasattr(result, "date")
        assert hasattr(result, "balance")
        assert hasattr(result, "status")
        assert hasattr(result, "verified")
        assert hasattr(result, "is_deleted")
        assert result.id is not None
