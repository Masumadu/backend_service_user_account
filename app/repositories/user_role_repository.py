from app.core.repository import SQLBaseRepository
from app.models import UserRoleModel


class UserRoleRepository(SQLBaseRepository):
    model = UserRoleModel
