from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class TestSuite(BaseModel):
    __tablename__ = "test_suites"

    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    execution_mode: Mapped[str] = mapped_column(String(20), default="sequential")

    # Relationships
    project = relationship("Project", back_populates="test_suites")
    suite_cases = relationship("SuiteCase", back_populates="test_suite", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="test_suite", cascade="all, delete-orphan")
    test_executions = relationship("TestExecution", back_populates="test_suite")


class SuiteCase(BaseModel):
    __tablename__ = "suite_cases"

    suite_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False
    )
    test_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    test_suite = relationship("TestSuite", back_populates="suite_cases")
    test_case = relationship("TestCase", back_populates="suite_cases")
