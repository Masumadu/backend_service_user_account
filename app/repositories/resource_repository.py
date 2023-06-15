from app.core.repository import SQLBaseRepository
from app.models import ResourceModel


class ResourceRepository(SQLBaseRepository):
    model = ResourceModel
