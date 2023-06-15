import uuid

import sqlalchemy as sa

from app.core.database import Base
from app.utils import GUID


class UserRoleModel(Base):
    __tablename__ = "user_roles"
    id = sa.Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(GUID, sa.ForeignKey("users.id"), nullable=False, index=True)
    role_id = sa.Column(GUID, sa.ForeignKey("roles.id"), nullable=False, index=True)
    created_by = sa.Column(sa.String)
    updated_by = sa.Column(sa.String)
    deleted_by = sa.Column(sa.String)
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
    deleted_at = sa.Column(sa.DateTime(timezone=True))
    __table_args__ = (sa.Index("user_role_index", "user_id", "role_id", unique=True),)
