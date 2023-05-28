from abc import ABC
from typing import Generic, Optional, Sequence, Type, TypeVar

from fastapi import Query
from fastapi_pagination import Params as PaginationParams
from fastapi_pagination.bases import AbstractPage, AbstractParams

T = TypeVar("T")
C = TypeVar("C")


class BasePage(AbstractPage[T], Generic[T], ABC):
    data: Sequence[T]


class Params(PaginationParams):
    size: int = Query(50, alias="limit", ge=1, le=100, description="Page size")


class Page(BasePage[T], Generic[T]):
    count: int
    __params_type__ = Params

    @classmethod
    def create(
        cls: Type[C],
        items: Sequence[T],
        params: AbstractParams,
        total: Optional[int] = None,
    ) -> C:
        if not isinstance(params, Params):
            raise ValueError("Page should be used with Params")

        return Page(data=items, count=len(items))
