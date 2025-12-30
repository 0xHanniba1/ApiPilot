from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Environment(BaseModel):
    __tablename__ = "environments"

    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    project = relationship("Project", back_populates="environments")
    variables = relationship("EnvVariable", back_populates="environment", cascade="all, delete-orphan")
    test_executions = relationship("TestExecution", back_populates="environment")
    schedules = relationship("Schedule", back_populates="environment")


class EnvVariable(BaseModel):
    __tablename__ = "env_variables"

    environment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    environment = relationship("Environment", back_populates="variables")
