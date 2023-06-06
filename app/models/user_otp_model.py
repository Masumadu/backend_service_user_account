import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func

from app.core.database import Base
from app.utils import GUID


class UserOtpModel(Base):
    __tablename__ = "users_otp"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    otp_code = Column(String(), nullable=True, index=True)
    otp_code_expiration = Column(DateTime(timezone=True), nullable=True)
    sec_token = Column(String(), nullable=True)
    sec_token_expiration = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(GUID)
    updated_by = Column(GUID)
    deleted_by = Column(String)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True))
