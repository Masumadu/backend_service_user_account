from app.core.repository import SQLBaseRepository
from app.models import PermissionModel


class PermissionRepository(SQLBaseRepository):
    model = PermissionModel
