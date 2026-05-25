from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class TaskAttemptModel(Base):
    __tablename__ = 'task_attempts'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'))
    student_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    submitted_answer: Mapped[str] = mapped_column(Text)
    attempt_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50))
    awarded_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    task = relationship('TaskModel', back_populates='attempts')