import uuid

import sqlalchemy as sa
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Query, relationship

from app import constants
from app.core.database import Base, db
from app.enums import SortResultEnum
from app.utils import GUID, Params


class RoleModel(Base):
    __tablename__ = "roles"
    id = sa.Column(GUID, primary_key=True, default=uuid.uuid4)
    name = sa.Column(sa.String, nullable=False, unique=True)
    description = sa.Column(sa.String)
    is_active = sa.Column(sa.Boolean, nullable=False)
    created_by = sa.Column(GUID, nullable=False)
    updated_by = sa.Column(GUID, nullable=False)
    deleted_by = sa.Column(GUID)
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
    user_role = relationship("UserRoleModel", backref="role")
    role_permission = relationship("RolePermissionModel", backref="role")

    @classmethod
    def search(cls, keyword: str) -> Query:
        """
        Search for samples matching a keyword.

        :param keyword: The keyword to search for.
        :return: The query result.
        :rtype: Query
        """
        result = db.query(RoleModel).filter(
            sa.or_(
                RoleModel.name.ilike(f"%{keyword}%"),
                RoleModel.description.ilike(f"%{keyword}%"),
            )
        )

        return result

    @classmethod
    def filter(cls, query_result: Query, filter_param: dict) -> Query:
        """
        Apply filters to the query result.

        :param query_result: The query result to filter.
        :param filter_param: The filter parameters.
        :return: The filtered query result.
        :rtype: Query
        """
        assert isinstance(filter_param, dict), constants.ASSERT_DICT_OBJECT

        result = query_result.filter_by(**filter_param)

        return result

    @classmethod
    def sort(cls, query_result: Query, sort_in: SortResultEnum, order_by: str) -> Query:
        """
        Sort the query result.

        :param query_result: The query result to sort.
        :param sort_in: The sorting direction.
        :param order_by: The attribute to order by.
        :return: The sorted query result.
        :rtype: Query
        """
        assert query_result, constants.ASSERT_NULL_OBJECT
        assert sort_in, constants.ASSERT_NULL_OBJECT

        if order_by and hasattr(RoleModel, order_by):
            if sort_in == SortResultEnum.asc:
                query_result = query_result.order_by(
                    sa.asc(getattr(RoleModel, order_by))
                )
            else:
                query_result = query_result.order_by(
                    sa.desc(getattr(RoleModel, order_by))
                )

        return query_result

    @classmethod
    def paginate(cls, query_result: Query, pagination: Params) -> Query:
        """
        Paginate the query result.

        :param query_result: The query result to paginate.
        :param pagination: The pagination parameters.
        :return: The paginated query result.
        :rtype: Query
        """
        assert query_result, constants.ASSERT_NULL_OBJECT

        result = paginate(query_result, params=pagination)

        return result
