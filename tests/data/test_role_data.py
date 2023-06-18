import uuid

from .test_user_data import UserTestData


class RoleTestData(UserTestData):
    @property
    def existing_role(self):
        return {
            "id": "19a174f9-02d6-46f5-bd20-34ec86aa9053",
            "name": "admin",
            "description": "string",
            "is_active": True,
            "created_by": uuid.uuid4(),
            "updated_by": uuid.uuid4(),
        }

    @property
    def existing_user_role(self):
        return {
            "user_id": self.existing_user.get("id"),
            "role_id": self.existing_role.get("id"),
        }

    @property
    def create_role(self):
        return {"name": "user", "description": "string", "is_active": True}

    @property
    def assign_role_to_user(self):
        return {
            "user_id": self.existing_user.get("id"),
            "role_id": self.existing_role.get("id"),
        }

    @property
    def assign_permission_to_role(self):
        return {"role_id": self.existing_role.get("id")}
