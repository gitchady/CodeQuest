from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.base import Base


class TestCaseModel(Base):
    __tablename__ = 'test_cases'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code_task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('code_tasks.id', ondelete='CASCADE'),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default='')