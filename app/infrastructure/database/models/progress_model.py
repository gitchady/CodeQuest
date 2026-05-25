from sqlalchemy import ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.base import Base


class ProgressModel(Base):
    __tablename__ = 'progress'
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='uq_progress_student_course'),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    course_id: Mapped[str] = mapped_column(ForeignKey('courses.id', ondelete='CASCADE'))

    completed_code_task_ids: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON()),
        default=list,
    )

    completed_task_ids: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON()),
        default=list,
    )

    completed_question_ids: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON()),
        default=list,
    )
    completed_section_ids: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON()),
        default=list,
    )
    completed_module_ids: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON()),
        default=list,
    )
    total_points: Mapped[int] = mapped_column(Integer, default=0)
