import uuid
from datetime import datetime
from typing import List, Union

from pydantic import BaseModel

from .resource_schema import PermissionSchema


class RolePermissionSchema(BaseModel):
    id: uuid.UUID
    permission: PermissionSchema
    created_by: Union[str, None]
    updated_by: Union[str, None]
    deleted_by: Union[str, None]
    created_at: datetime
    updated_at: datetime
    deleted_at: Union[datetime, None]

    class Config:
        orm_mode = True


class RoleSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    is_active: bool
    role_permission: List[RolePermissionSchema]
    created_by: uuid.UUID
    updated_by: uuid.UUID
    deleted_by: Union[uuid.UUID, None]
    created_at: datetime
    updated_at: datetime
    deleted_at: Union[datetime, None]

    class Config:
        orm_mode = True


class CreateRoleSchema(BaseModel):
    name: str
    description: Union[str, None]
    is_active: bool


class AssignUserRoleSchema(BaseModel):
    user_id: str
    role_id: str


class AssignRolePermissionSchema(BaseModel):
    role_id: str
    permission_id: str
