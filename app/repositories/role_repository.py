from app.core.repository import SQLBaseRepository
from app.models import RoleModel


class RoleRepository(SQLBaseRepository):
    model = RoleModel
