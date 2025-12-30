from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class TestExecution(BaseModel):
    __tablename__ = "test_executions"

    suite_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_suites.id", ondelete="SET NULL"), nullable=True
    )
    test_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_cases.id", ondelete="SET NULL"), nullable=True
    )
    environment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("environments.id"), nullable=False
    )
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    test_suite = relationship("TestSuite", back_populates="test_executions")
    environment = relationship("Environment", back_populates="test_executions")
    details = relationship("ExecutionDetail", back_populates="execution", cascade="all, delete-orphan")


class ExecutionDetail(BaseModel):
    __tablename__ = "execution_details"

    execution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_executions.id", ondelete="CASCADE"), nullable=False
    )
    test_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_cases.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    request_url: Mapped[str] = mapped_column(Text, nullable=True)
    request_method: Mapped[str] = mapped_column(String(10), nullable=True)
    request_headers: Mapped[dict] = mapped_column(JSONB, nullable=True)
    request_body: Mapped[str] = mapped_column(Text, nullable=True)
    response_status_code: Mapped[int] = mapped_column(Integer, nullable=True)
    response_headers: Mapped[dict] = mapped_column(JSONB, nullable=True)
    response_body: Mapped[str] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    assertion_results: Mapped[dict] = mapped_column(JSONB, nullable=True)
    extractor_results: Mapped[dict] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    execution = relationship("TestExecution", back_populates="details")
    test_case = relationship("TestCase", back_populates="execution_details")
