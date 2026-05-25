from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class CourseModel(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    author_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String)

    author = relationship("UserModel", back_populates="courses")

    modules = relationship(
        "ModuleModel",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="ModuleModel.position",
    )
