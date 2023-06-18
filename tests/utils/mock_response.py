import uuid


class MockResponse:
    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json


class MockSideEffects:
    status_code = 200
    json = None

    # noinspection PyMethodMayBeStatic
    def mock_decode_token(self, username):
        return {"user_id": str(uuid.uuid4()), "username": username}
