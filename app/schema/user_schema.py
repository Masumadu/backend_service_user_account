import re
import uuid
from datetime import date, datetime
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, validator

from app.core.exceptions import AppException
from app.enums import RegularExpression, StatusEnum


def phone_validator(cls, v, values, **kwargs):
    if not re.match(RegularExpression.phone_number.value, v):
        raise AppException.ValidationException(error_message="invalid phone format")
    return v


def password_validator(cls, v, values, **kwargs):
    if not re.match(RegularExpression.pin.value, v):
        raise AppException.ValidationException(error_message="invalid password format")
    return v


class UserSchema(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str
    birth_date: date
    national_id: str
    id_expiration: date
    is_verified: bool
    last_active: Union[datetime, None]
    auth_provider_id: Union[str, None]
    status: StatusEnum
    is_deleted: bool
    meta_data: Union[dict, None]
    created_at: datetime
    updated_at: datetime
    deleted_at: Union[datetime, None]

    class Config:
        orm_mode = True


class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str
    password: str
    birth_date: Optional[date] = None
    national_id: str
    id_expiration: date

    _phone_validator = validator("phone", allow_reuse=True)(phone_validator)
    _password_validator = validator("password", allow_reuse=True)(password_validator)


class UpdateUserSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    national_id: Optional[str] = None
    id_expiration: Optional[date] = None


class UserLoginSchema(BaseModel):
    username: str
    password: str

    _password_validator = validator("password", allow_reuse=True)(password_validator)


class UserLoginResponseSchema(BaseModel):
    user_id: uuid.UUID
    access_token: str
    refresh_token: str


class UserTokenRefreshSchema(BaseModel):
    user_id: uuid.UUID
    refresh_token: str


class UserPhoneVerificationSchema(BaseModel):
    new_phone: str

    _phone_validator = validator("new_phone", allow_reuse=True)(phone_validator)


class UserChangePhoneSchema(UserPhoneVerificationSchema):
    sec_token: str


class UserIdSchema(BaseModel):
    user_id: uuid.UUID


class UserResetPasswordSchema(BaseModel):
    user_id: uuid.UUID
    sec_token: str
    new_password: str

    _password_validator = validator("new_password", allow_reuse=True)(password_validator)


class UserChangePasswordSchema(BaseModel):
    sec_token: str
    new_password: str
    old_password: str

    _password_validator = validator("old_password", "new_password", allow_reuse=True)(
        password_validator
    )


class UserSendOtpSchema(BaseModel):
    user_id: Optional[uuid.UUID] = None
    phone: Optional[str] = None

    _phone_validator = validator("phone", allow_reuse=True)(phone_validator)


class UserOtpConfirmationSchema(UserIdSchema):
    otp_code: str


class UserOtpConfirmationResponseSchema(UserIdSchema):
    sec_token: str
