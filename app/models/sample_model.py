import uuid

import sqlalchemy as sa
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Query

from app import constants
from app.core.database import Base, db
from app.enums import QuerySortEnum, StatusEnum
from app.utils import GUID, Params


class SampleModel(Base):
    """
    Sample Model.

    Represents a sample table in the database.
    """

    __tablename__ = "sample_table"
    id = sa.Column(GUID, primary_key=True, default=uuid.uuid4)
    name = sa.Column(sa.String, nullable=False)
    country = sa.Column(sa.String, nullable=False)
    agent = sa.Column(sa.String, nullable=False)
    date = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    balance = sa.Column(sa.Numeric(10, 2), nullable=False)
    status = sa.Column(
        sa.Enum(StatusEnum, name="status"),
        default=StatusEnum.proposal,
        nullable=False,
    )
    verified = sa.Column(sa.Boolean, nullable=False, default=False)
    is_deleted = sa.Column(sa.Boolean, nullable=False, default=False)

    @classmethod
    def search(cls, keyword: str) -> Query:
        """
        Search for samples matching a keyword.

        :param keyword: The keyword to search for.
        :return: The query result.
        :rtype: Query
        """
        result = db.query(SampleModel).filter(
            sa.or_(
                SampleModel.name.ilike(f"%{keyword}%"),
                SampleModel.country.ilike(f"%{keyword}%"),
                SampleModel.agent.ilike(f"%{keyword}%"),
                sa.cast(SampleModel.balance, sa.String).ilike(f"%{keyword}%"),
                sa.cast(SampleModel.status, sa.String).ilike(f"%{keyword}%"),
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
    def sort(cls, query_result: Query, sort_in: QuerySortEnum, sort_by: str) -> Query:
        """
        Sort the query result.

        :param query_result: The query result to sort.
        :param sort_in: The sorting direction.
        :param sort_by: The attribute to sort by.
        :return: The sorted query result.
        :rtype: Query
        """
        assert query_result, constants.ASSERT_NULL_OBJECT
        assert sort_in, constants.ASSERT_NULL_OBJECT

        if sort_by and hasattr(SampleModel, sort_by):
            if sort_in == QuerySortEnum.asc:
                query_result = query_result.order_by(
                    sa.asc(getattr(SampleModel, sort_by))
                )
            else:
                query_result = query_result.order_by(
                    sa.desc(getattr(SampleModel, sort_by))
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
