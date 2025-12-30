from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Schedule(BaseModel):
    __tablename__ = "schedules"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    suite_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False
    )
    environment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("environments.id"), nullable=False
    )
    cron_expression: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_failure: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_emails: Mapped[str] = mapped_column(Text, nullable=True)
    last_run_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    test_suite = relationship("TestSuite", back_populates="schedules")
    environment = relationship("Environment", back_populates="schedules")
