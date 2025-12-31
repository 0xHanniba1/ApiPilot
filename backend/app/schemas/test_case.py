from datetime import datetime
from pydantic import BaseModel, Field


# Assertion Schemas
class AssertionCreate(BaseModel):
    name: str | None = Field(None, max_length=100)
    type: str = Field(..., max_length=30)  # status_code/json_path/header/response_time/contains
    expression: str = Field(..., max_length=500)
    operator: str = Field(..., max_length=20)  # eq/ne/gt/lt/gte/lte/contains/not_contains/regex
    expected_value: str | None = None
    sort_order: int = 0


class AssertionUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    type: str | None = Field(None, max_length=30)
    expression: str | None = Field(None, max_length=500)
    operator: str | None = Field(None, max_length=20)
    expected_value: str | None = None
    sort_order: int | None = None


class AssertionResponse(BaseModel):
    id: int
    test_case_id: int
    name: str | None
    type: str
    expression: str
    operator: str
    expected_value: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Extractor Schemas
class ExtractorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    source: str = Field(..., max_length=20)  # body/header/cookie
    expression: str = Field(..., max_length=500)
    variable_name: str = Field(..., min_length=1, max_length=100)
    default_value: str | None = None
    sort_order: int = 0


class ExtractorUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    source: str | None = Field(None, max_length=20)
    expression: str | None = Field(None, max_length=500)
    variable_name: str | None = Field(None, min_length=1, max_length=100)
    default_value: str | None = None
    sort_order: int | None = None


class ExtractorResponse(BaseModel):
    id: int
    test_case_id: int
    name: str
    source: str
    expression: str
    variable_name: str
    default_value: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Test Case Schemas
class TestCaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    method: str = Field(..., max_length=10)  # GET/POST/PUT/DELETE/PATCH
    path: str = Field(..., min_length=1, max_length=500)
    headers: dict = Field(default_factory=dict)
    params: dict = Field(default_factory=dict)
    body_type: str = "none"  # none/json/form/form-data/raw
    body_content: str | None = None
    pre_script: str | None = None
    post_script: str | None = None
    timeout: int = 30
    retry_count: int = 0
    is_active: bool = True
    sort_order: int = 0


class TestCaseUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    method: str | None = Field(None, max_length=10)
    path: str | None = Field(None, min_length=1, max_length=500)
    headers: dict | None = None
    params: dict | None = None
    body_type: str | None = None
    body_content: str | None = None
    pre_script: str | None = None
    post_script: str | None = None
    timeout: int | None = None
    retry_count: int | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class TestCaseResponse(BaseModel):
    id: int
    module_id: int
    name: str
    description: str | None
    method: str
    path: str
    headers: dict
    params: dict
    body_type: str
    body_content: str | None
    pre_script: str | None
    post_script: str | None
    timeout: int
    retry_count: int
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestCaseListResponse(BaseModel):
    id: int
    module_id: int
    name: str
    method: str
    path: str
    is_active: bool
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TestCaseDetailResponse(TestCaseResponse):
    assertions: list[AssertionResponse] = []
    extractors: list[ExtractorResponse] = []
