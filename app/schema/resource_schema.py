import uuid
from datetime import datetime
from typing import List, Union

from pydantic import BaseModel


class PermissionSchema(BaseModel):
    id: uuid.UUID
    resource_id: uuid.UUID
    mode: str
    description: Union[str, None]
    created_by: Union[str, None]
    updated_by: Union[str, None]
    deleted_by: Union[str, None]
    created_at: datetime
    updated_at: datetime
    deleted_at: Union[datetime, None]

    class Config:
        orm_mode = True


class ResourceSchema(BaseModel):
    id: uuid.UUID
    type: str
    description: str
    permissions: List[PermissionSchema]
    created_by: Union[str, None]
    updated_by: Union[str, None]
    deleted_by: Union[str, None]
    created_at: datetime
    updated_at: datetime
    deleted_at: Union[datetime, None]

    class Config:
        orm_mode = True


class CreateResourceSchema(BaseModel):
    type: str
    description: Union[str, None]


class ResourcePermissionSchema(BaseModel):
    resource_id: uuid.UUID
    mode: str
    description: Union[str, None]
