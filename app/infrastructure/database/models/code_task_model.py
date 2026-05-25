from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class CodeTaskModel(Base):
    __tablename__ = 'code_tasks'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    section_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('sections.id', ondelete='CASCADE'),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    starter_code: Mapped[str] = mapped_column(Text, nullable=False, default='')
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_points: Mapped[int] = mapped_column(Integer, nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, nullable=False)

    section = relationship('SectionModel', back_populates='code_tasks')