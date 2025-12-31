from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.test_case import TestCaseListResponse


# Suite Case Schemas
class SuiteCaseCreate(BaseModel):
    test_case_id: int
    sort_order: int = 0


class SuiteCaseResponse(BaseModel):
    id: int
    suite_id: int
    test_case_id: int
    sort_order: int

    model_config = {"from_attributes": True}


class SuiteCaseOrderUpdate(BaseModel):
    case_orders: list[dict]  # [{"test_case_id": 1, "sort_order": 0}, ...]


# Test Suite Schemas
class TestSuiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    execution_mode: str = "sequential"  # sequential/parallel


class TestSuiteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    execution_mode: str | None = None


class TestSuiteResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: str | None
    execution_mode: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestSuiteListResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: str | None
    execution_mode: str
    case_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class SuiteCaseDetailResponse(BaseModel):
    id: int
    suite_id: int
    test_case_id: int
    sort_order: int
    test_case: TestCaseListResponse

    model_config = {"from_attributes": True}


class TestSuiteDetailResponse(TestSuiteResponse):
    cases: list[SuiteCaseDetailResponse] = []
