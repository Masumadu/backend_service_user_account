import uuid


class ResourceTestData:
    @property
    def existing_resource(self):
        return {
            "id": "19a174f9-02d6-46f5-bd20-34ec86aa9053",
            "type": "admin",
            "description": "string",
            "created_by": uuid.uuid4(),
            "updated_by": uuid.uuid4(),
        }

    @property
    def existing_permission(self):
        return {
            "id": "67fb129c-d5e5-4fa5-912a-5b270e1ba88a",
            "resource_id": self.existing_resource.get("id"),
            "mode": "write",
            "created_by": uuid.uuid4(),
            "updated_by": uuid.uuid4(),
        }

    @property
    def assign_permission_to_resource(self):
        return {"mode": "write", "description": "description"}

    @property
    def create_resource(self):
        return {
            "type": "user",
            "description": "string",
        }
