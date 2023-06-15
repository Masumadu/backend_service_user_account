from app.core.repository import SQLBaseRepository
from app.models import RolePermissionModel


class RolePermissionRepository(SQLBaseRepository):
    model = RolePermissionModel
