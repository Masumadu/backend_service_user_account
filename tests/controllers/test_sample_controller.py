import uuid

import pytest
from fastapi_pagination import Page, Params

from app.core.exceptions import AppException
from app.enums import QuerySortEnum
from app.models import SampleModel
from tests.base_test_case import BaseTestCase


class TestSampleController(BaseTestCase):
    @pytest.mark.controller
    def test_get_all_resource(self, test_app, caplog):
        result = self.sample_controller.get_all_resource(
            search="",
            sort_by=None,
            sort_in=QuerySortEnum.asc,
            is_deleted=None,
            pagination=Params(),
        )

        assert result
        assert isinstance(result, Page)
        assert isinstance(result.items, list)
        assert all([isinstance(obj, SampleModel) for obj in result.items])

    @pytest.mark.controller
    def test_get_resource(self, test_app, caplog):
        result = self.sample_controller.get_resource(obj_id=self.sample_model.id)

        assert result
        assert isinstance(result, SampleModel)
        with pytest.raises(AppException.NotFoundException) as not_found:
            self.sample_controller.get_resource(obj_id=uuid.uuid4())
        assert not_found.value.status_code == 404
        assert "does not exist" in not_found.value.error_message

    @pytest.mark.controller
    def test_create_resource(self, test_app):
        result = self.sample_controller.create_resource(
            obj_data=self.sample_test_data.create_sample
        )

        assert result
        assert isinstance(result, SampleModel)
        assert self.db_instance.query(SampleModel).count() == 2

    @pytest.mark.controller
    def test_update_resource(self, test_app):
        result = self.sample_controller.update_resource(
            obj_id=self.sample_model.id, obj_data=self.sample_test_data.update_sample
        )

        assert result
        assert isinstance(result, SampleModel)
        assert result.status.value == self.sample_test_data.update_sample.get("status")

    @pytest.mark.controller
    def test_delete_resource(self, test_app):
        result = self.sample_controller.delete(obj_id=self.sample_model.id)

        assert self.sample_model.is_deleted is True
        assert result is None
