import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.enums import StatusEnum


class SampleSchema(BaseModel):
    id: uuid.UUID
    name: str
    country: str
    agent: str
    date: datetime
    balance: Decimal
    status: StatusEnum
    verified: bool
    is_deleted: bool

    class Config:
        orm_mode = True


class CreateSampleSchema(BaseModel):
    name: str
    country: str
    agent: str
    date: datetime
    balance: Decimal


class UpdateSampleSchema(BaseModel):
    name: str = None
    country: str = None
    agent: str = None
    date: datetime = None
    balance: Decimal = None
    status: StatusEnum = None
    verified: bool = None
    is_deleted: bool = None
