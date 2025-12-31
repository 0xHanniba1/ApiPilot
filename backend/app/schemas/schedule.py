from datetime import datetime
from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    suite_id: int
    environment_id: int
    cron_expression: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True
    notify_on_failure: bool = True
    notify_emails: str | None = None  # comma separated


class ScheduleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    suite_id: int | None = None
    environment_id: int | None = None
    cron_expression: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None
    notify_on_failure: bool | None = None
    notify_emails: str | None = None


class ScheduleResponse(BaseModel):
    id: int
    name: str
    suite_id: int
    environment_id: int
    cron_expression: str
    is_active: bool
    notify_on_failure: bool
    notify_emails: str | None
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScheduleListResponse(BaseModel):
    id: int
    name: str
    suite_id: int
    suite_name: str | None = None
    environment_id: int
    environment_name: str | None = None
    cron_expression: str
    is_active: bool
    last_run_at: datetime | None
    next_run_at: datetime | None

    model_config = {"from_attributes": True}
