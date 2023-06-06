from app.core.repository import SQLBaseRepository
from app.models import UserOtpModel


class UserOtpRepository(SQLBaseRepository):
    model = UserOtpModel
