from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.base import Base


class CodeSubmissionModel(Base):
    __tablename__ = 'code_submissions'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code_task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('code_tasks.id', ondelete='CASCADE'),
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)