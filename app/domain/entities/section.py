from dataclasses import dataclass, field
from uuid import UUID
from collections.abc import Collection

from app.domain.exceptions import (
    InvalidSectionError,
    SectionQuestionAlreadyAttachedError,
    SectionQuestionNotAttachedError,
    SectionTaskAlreadyAttachedError,
    SectionTaskNotAttachedError, SectionCodeTaskAlreadyAttachedError,
    SectionCodeTaskNotAttachedError,
)


@dataclass(slots=True)
class Section:
    id: UUID
    module_id: UUID
    title: str
    description: str = ''
    position: int = 1
    lecture_ids: list[UUID] = field(default_factory=list)
    question_ids: list[UUID] = field(default_factory=list)
    task_ids: list[UUID] = field(default_factory=list)
    code_task_ids: list[UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidSectionError('Section title cannot be empty.')
        if self.position < 1:
            raise InvalidSectionError('Section position must be positive.')

    def update(self, title: str, description: str, position: int) -> None:
        self.title = title
        self.description = description
        self.position = position
        self._validate()

    def add_lecture(self, lecture_id: UUID) -> None:
        if lecture_id not in self.lecture_ids:
            self.lecture_ids.append(lecture_id)

    def remove_lecture(self, lecture_id: UUID) -> None:
        if lecture_id in self.lecture_ids:
            self.lecture_ids.remove(lecture_id)

    def add_question(self, question_id: UUID) -> None:
        if question_id in self.question_ids:
            raise SectionQuestionAlreadyAttachedError(
                'Section already has this question attached.'
            )
        self.question_ids.append(question_id)

    def remove_question(self, question_id: UUID) -> None:
        if question_id not in self.question_ids:
            raise SectionQuestionNotAttachedError(
                'Section does not have this question attached.'
            )
        self.question_ids.remove(question_id)

    def add_task(self, task_id: UUID) -> None:
        if task_id in self.task_ids:
            raise SectionTaskAlreadyAttachedError(
                'Section already has this task attached.'
            )
        self.task_ids.append(task_id)

    def remove_task(self, task_id: UUID) -> None:
        if task_id not in self.task_ids:
            raise SectionTaskNotAttachedError(
                'Section does not have this task attached.'
            )
        self.task_ids.remove(task_id)

    def has_questions(self) -> bool:
        return bool(self.question_ids)

    def has_tasks(self) -> bool:
        return bool(self.task_ids)

    def contains_question(self, question_id: UUID) -> bool:
        return question_id in self.question_ids

    def contains_task(self, task_id: UUID) -> bool:
        return task_id in self.task_ids

    def can_be_completed(self) -> bool:
        return bool(self.question_ids or self.task_ids or self.code_task_ids)

    def is_completed_by(
            self,
            completed_question_ids: Collection[UUID],
            completed_task_ids: Collection[UUID] | None = None,
            completed_code_task_ids: Collection[UUID] | None = None,
    ) -> bool:
        if not self.can_be_completed():
            return False

        completed_task_ids = completed_task_ids or ()
        completed_code_task_ids = completed_code_task_ids or ()

        return (
                all(question_id in completed_question_ids for question_id in self.question_ids)
                and all(task_id in completed_task_ids for task_id in self.task_ids)
                and all(code_task_id in completed_code_task_ids for code_task_id in self.code_task_ids)
        )

    def add_code_task(self, code_task_id: UUID) -> None:
        if code_task_id in self.code_task_ids:
            raise SectionCodeTaskAlreadyAttachedError(
                'Section already has this code task attached.'
            )
        self.code_task_ids.append(code_task_id)

    def remove_code_task(self, code_task_id: UUID) -> None:
        if code_task_id not in self.code_task_ids:
            raise SectionCodeTaskNotAttachedError(
                'Section does not have this code task attached.'
            )
        self.code_task_ids.remove(code_task_id)

    def has_code_tasks(self) -> bool:
        return bool(self.code_task_ids)

    def contains_code_task(self, code_task_id: UUID) -> bool:
        return code_task_id in self.code_task_ids