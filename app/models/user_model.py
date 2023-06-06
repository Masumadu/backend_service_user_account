import uuid

import sqlalchemy as sa
from fastapi_pagination.ext.sqlalchemy import paginate
from passlib.context import CryptContext
from sqlalchemy.orm import Query

from app import constants
from app.core.database import Base, db
from app.enums import SortResultEnum, StatusEnum
from app.utils import GUID, Params

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(Base):
    """
    Represents a users table in the database.
    """

    __tablename__ = "users"
    id = sa.Column(GUID, primary_key=True, default=uuid.uuid4)
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
    username = sa.Column(sa.String, nullable=False, unique=True, index=True)
    email = sa.Column(sa.String, nullable=False, unique=True, index=True)
    phone = sa.Column(sa.String, nullable=False, unique=True, index=True)
    birth_date = sa.Column(sa.Date)
    national_id = sa.Column(sa.String, nullable=False, unique=True, index=True)
    id_expiration = sa.Column(sa.Date, nullable=False)
    password = sa.Column(sa.String, nullable=False)
    is_verified = sa.Column(sa.Boolean, nullable=False, default=False)
    last_active = sa.Column(sa.DateTime)
    auth_provider_id = sa.Column(sa.String, unique=True, index=True)
    status = sa.Column(
        sa.Enum(StatusEnum, name="user_status"),
        default=StatusEnum.inactive,
        nullable=False,
    )
    is_deleted = sa.Column(sa.Boolean, nullable=False, default=False)
    meta_data = sa.Column(sa.String)
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

    @property
    def hash_password(self):
        return self.password

    @hash_password.setter
    def hash_password(self, password):
        self.password = pwd_context.hash(password)

    # noinspection PyMethodMayBeStatic
    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)

    @classmethod
    def search(cls, keyword: str) -> Query:
        """
        Search for samples matching a keyword.

        :param keyword: The keyword to search for.
        :return: The query result.
        :rtype: Query
        """
        result = db.query(UserModel).filter(
            sa.or_(
                UserModel.first_name.ilike(f"%{keyword}%"),
                UserModel.last_name.ilike(f"%{keyword}%"),
                UserModel.username.ilike(f"%{keyword}%"),
                UserModel.email.ilike(f"%{keyword}%"),
                sa.cast(UserModel.birth_date, sa.String).ilike(f"%{keyword}%"),
                UserModel.national_id.ilike(f"%{keyword}%"),
                sa.cast(UserModel.id_expiration, sa.String).ilike(f"%{keyword}%"),
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

        if order_by and hasattr(UserModel, order_by):
            if sort_in == SortResultEnum.asc:
                query_result = query_result.order_by(
                    sa.asc(getattr(UserModel, order_by))
                )
            else:
                query_result = query_result.order_by(
                    sa.desc(getattr(UserModel, order_by))
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
