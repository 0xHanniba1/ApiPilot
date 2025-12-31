from datetime import datetime
from pydantic import BaseModel, Field


# Environment Variable Schemas
class EnvVariableCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str | None = None
    description: str | None = None


class EnvVariableUpdate(BaseModel):
    key: str | None = Field(None, min_length=1, max_length=100)
    value: str | None = None
    description: str | None = None


class EnvVariableResponse(BaseModel):
    id: int
    environment_id: int
    key: str
    value: str | None
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# Environment Schemas
class EnvironmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    base_url: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    is_default: bool = False


class EnvironmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    base_url: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    is_default: bool | None = None


class EnvironmentResponse(BaseModel):
    id: int
    project_id: int
    name: str
    base_url: str
    description: str | None
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EnvironmentDetailResponse(EnvironmentResponse):
    variables: list[EnvVariableResponse] = []
