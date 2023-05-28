import pytest

from tests.base_test_case import BaseTestCase

BASE_URL = "/api/v1/sample-resource"


class TestSampleView(BaseTestCase):
    @pytest.mark.view
    def test_get_all_resource(self, test_app):
        response = test_app.get(f"{BASE_URL}/", params={"skip": 0, "limit": 10})
        response_data = response.json()
        assert response.status_code == 200
        assert response_data
        assert isinstance(response_data, dict)

    def test_get_resource(self, test_app):
        response = test_app.get(f"{BASE_URL}/{self.sample_model.id}")
        response_data = response.json()
        assert response.status_code == 200
        assert response_data
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_create_resource(self, test_app):
        response = test_app.post(
            f"{BASE_URL}/", json=self.sample_test_data.create_sample
        )
        response_data = response.json()
        assert response.status_code == 201
        assert response_data
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_update_resource(self, test_app):
        response = test_app.patch(
            f"{BASE_URL}/{self.sample_model.id}",
            json=self.sample_test_data.update_sample,
            headers=self.headers,
        )
        response_data = response.json()
        assert response.status_code == 200
        assert response_data
        assert isinstance(response_data, dict)

    @pytest.mark.view
    def test_delete_resource(self, test_app):
        response = test_app.delete(
            f"{BASE_URL}/{self.sample_model.id}", headers=self.headers
        )
        assert response.status_code == 204
