from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: T | None = None


class PaginationData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class PaginationResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: PaginationData[T]


def success(data: Any = None, message: str = "success"):
    return ResponseModel(code=0, message=message, data=data)


def error(code: int, message: str, detail: str | None = None):
    response = {"code": code, "message": message}
    if detail:
        response["detail"] = detail
    return response


def paginate(items: list, total: int, page: int, page_size: int):
    return PaginationResponse(
        data=PaginationData(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    )
