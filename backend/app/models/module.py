from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Module(BaseModel):
    __tablename__ = "modules"

    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("modules.id", ondelete="SET NULL"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    project = relationship("Project", back_populates="modules")
    parent = relationship("Module", remote_side="Module.id", backref="children")
    test_cases = relationship("TestCase", back_populates="module", cascade="all, delete-orphan")
