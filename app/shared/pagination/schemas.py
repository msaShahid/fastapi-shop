from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PageParams(BaseModel):

    page: int = Query(default=1, ge=1)
    page_size: int = Query(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class ProductQueryParams(PageParams):
    category_id: int | None = Query(default=None)
    search: str | None = Query(default=None, max_length=100)
    min_price: int | None = Query(default=None, ge=0)
    max_price: int | None = Query(default=None, ge=0)
    sort: str = Query(default="-created_at", pattern="^-?(created_at|price_cents|name)$")

class PaginatedResponse(BaseModel, Generic[T]):

    items: list[T]
    total: int
    page: int
    page_size: int
