from datetime import datetime

from app.enums import StatusEnum


class SampleTestData:
    @property
    def exiting_sample(self):
        return {
            "name": "test name",
            "country": "test country",
            "agent": "test agent",
            "date": datetime.utcnow(),
            "balance": 45.98,
            "status": StatusEnum.proposal,
            "verified": False,
            "is_deleted": False,
        }

    @property
    def create_sample(self):
        return {
            "name": "new name",
            "country": "new country",
            "agent": "new agent",
            "date": str(datetime.utcnow()),
            "balance": 345678.67,
            "status": StatusEnum.unqualified.value,
            "verified": True,
            "is_deleted": False,
        }

    @property
    def update_sample(self):
        return {
            "verified": True,
            "status": StatusEnum.qualified.value,
        }
