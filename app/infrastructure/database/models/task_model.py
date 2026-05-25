from sqlalchemy import ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class TaskModel(Base):
    __tablename__ = 'tasks'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    section_id: Mapped[str] = mapped_column(ForeignKey('sections.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(255))
    statement: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)
    check_type: Mapped[str] = mapped_column(String(50))
    expected_answer: Mapped[str] = mapped_column(Text, default='')
    accepted_answers: Mapped[list[str]] = mapped_column(JSON, default=list)
    answer_pattern: Mapped[str] = mapped_column(Text, default='')
    max_attempts: Mapped[int] = mapped_column(Integer)
    reward_points: Mapped[int] = mapped_column(Integer)

    section = relationship('SectionModel', back_populates='tasks')
    attempts = relationship(
        'TaskAttemptModel',
        back_populates='task',
        cascade='all, delete-orphan',
        order_by='TaskAttemptModel.attempt_number',
    )