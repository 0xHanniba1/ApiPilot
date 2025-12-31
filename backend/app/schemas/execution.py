from datetime import datetime
from pydantic import BaseModel


# Execution Detail Schemas
class ExecutionDetailResponse(BaseModel):
    id: int
    execution_id: int
    test_case_id: int
    test_case_name: str | None = None
    status: str  # passed/failed/error/skipped
    request_url: str | None
    request_method: str | None
    request_headers: dict | None
    request_body: str | None
    response_status_code: int | None
    response_headers: dict | None
    response_body: str | None
    duration_ms: int | None
    assertion_results: list | None
    extractor_results: dict | None
    error_message: str | None
    executed_at: datetime | None

    model_config = {"from_attributes": True}


# Test Execution Schemas
class ExecuteCaseRequest(BaseModel):
    test_case_id: int
    environment_id: int


class ExecuteSuiteRequest(BaseModel):
    suite_id: int
    environment_id: int


class DebugExecuteRequest(BaseModel):
    environment_id: int
    method: str
    path: str
    headers: dict = {}
    params: dict = {}
    body_type: str = "none"
    body_content: str | None = None


class TestExecutionResponse(BaseModel):
    id: int
    suite_id: int | None
    test_case_id: int | None
    environment_id: int
    trigger_type: str  # manual/schedule/api
    status: str  # pending/running/passed/failed/error
    total_count: int
    passed_count: int
    failed_count: int
    skipped_count: int
    duration_ms: int | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TestExecutionListResponse(BaseModel):
    id: int
    suite_id: int | None
    suite_name: str | None = None
    test_case_id: int | None
    test_case_name: str | None = None
    environment_id: int
    environment_name: str | None = None
    trigger_type: str
    status: str
    total_count: int
    passed_count: int
    failed_count: int
    duration_ms: int | None
    started_at: datetime | None
    finished_at: datetime | None

    model_config = {"from_attributes": True}


class TestExecutionDetailResponse(TestExecutionResponse):
    suite_name: str | None = None
    test_case_name: str | None = None
    environment_name: str | None = None
    details: list[ExecutionDetailResponse] = []


# Debug Response
class DebugResponse(BaseModel):
    request_url: str
    request_method: str
    request_headers: dict
    request_body: str | None
    response_status_code: int
    response_headers: dict
    response_body: str
    duration_ms: int
