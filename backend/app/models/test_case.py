from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class TestCase(BaseModel):
    __tablename__ = "test_cases"

    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    headers: Mapped[dict] = mapped_column(JSONB, default=dict)
    params: Mapped[dict] = mapped_column(JSONB, default=dict)
    body_type: Mapped[str] = mapped_column(String(20), default="none")
    body_content: Mapped[str] = mapped_column(Text, nullable=True)
    pre_script: Mapped[str] = mapped_column(Text, nullable=True)
    post_script: Mapped[str] = mapped_column(Text, nullable=True)
    timeout: Mapped[int] = mapped_column(Integer, default=30)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    module = relationship("Module", back_populates="test_cases")
    assertions = relationship("Assertion", back_populates="test_case", cascade="all, delete-orphan")
    extractors = relationship("Extractor", back_populates="test_case", cascade="all, delete-orphan")
    suite_cases = relationship("SuiteCase", back_populates="test_case", cascade="all, delete-orphan")
    execution_details = relationship("ExecutionDetail", back_populates="test_case")


class Assertion(BaseModel):
    __tablename__ = "assertions"

    test_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    expression: Mapped[str] = mapped_column(String(500), nullable=False)
    operator: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_value: Mapped[str] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    test_case = relationship("TestCase", back_populates="assertions")


class Extractor(BaseModel):
    __tablename__ = "extractors"

    test_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    expression: Mapped[str] = mapped_column(String(500), nullable=False)
    variable_name: Mapped[str] = mapped_column(String(100), nullable=False)
    default_value: Mapped[str] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    test_case = relationship("TestCase", back_populates="extractors")
