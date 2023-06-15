import uuid

import sqlalchemy as sa

from app.core.database import Base
from app.utils import GUID


class RolePermissionModel(Base):
    __tablename__ = "role_permissions"
    id = sa.Column(GUID, primary_key=True, default=uuid.uuid4)
    permission_id = sa.Column(
        GUID, sa.ForeignKey("permissions.id"), nullable=False, index=True
    )
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
    __table_args__ = (
        sa.Index("role_permission_index", "role_id", "permission_id", unique=True),
    )
