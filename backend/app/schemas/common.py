from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: T | None = None


class PageData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class PageResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: PageData[T]


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


class IdResponse(BaseModel):
    id: int
