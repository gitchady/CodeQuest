from dataclasses import dataclass, field
from uuid import UUID

from app.domain.entities.task_attempt import TaskAttempt
from app.domain.exceptions import InvalidProgressError

from app.domain.entities.section import Section
from app.domain.entities.module import Module
from app.domain.entities.question_attempt import QuestionAttempt


@dataclass(slots=True)
class Progress:
    id: UUID
    student_id: UUID
    course_id: UUID
    completed_code_task_ids: list[UUID] = field(default_factory=list)
    completed_task_ids: list[UUID] = field(default_factory=list)
    completed_question_ids: list[UUID] = field(default_factory=list)
    completed_section_ids: list[UUID] = field(default_factory=list)
    completed_module_ids: list[UUID] = field(default_factory=list)
    total_points: int = 0

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if len(self.completed_question_ids) != len(set(self.completed_question_ids)):
            raise InvalidProgressError('Progress cannot contain duplicate completed questions.')
        if len(self.completed_task_ids) != len(set(self.completed_task_ids)):
            raise InvalidProgressError('Progress cannot contain duplicate completed tasks.')
        if len(self.completed_section_ids) != len(set(self.completed_section_ids)):
            raise InvalidProgressError('Progress cannot contain duplicate completed sections.')
        if len(self.completed_module_ids) != len(set(self.completed_module_ids)):
            raise InvalidProgressError('Progress cannot contain duplicate completed modules.')
        if self.total_points < 0:
            raise InvalidProgressError('Progress total points cannot be negative.')
        if len(self.completed_code_task_ids) != len(set(self.completed_code_task_ids)):
            raise InvalidProgressError('Progress cannot contain duplicate completed code tasks.')

    def has_completed_question(self, question_id: UUID) -> bool:
        return question_id in self.completed_question_ids

    def has_completed_section(self, section_id: UUID) -> bool:
        return section_id in self.completed_section_ids

    def mark_question_completed(self, question_id: UUID) -> None:
        if question_id not in self.completed_question_ids:
            self.completed_question_ids.append(question_id)

    def mark_section_completed(self, section_id: UUID) -> None:
        if section_id not in self.completed_section_ids:
            self.completed_section_ids.append(section_id)

    def apply_correct_attempt(self, attempt: QuestionAttempt) -> bool:
        if attempt.student_id != self.student_id:
            raise InvalidProgressError('Question attempt does not belong to this student.')

        if not attempt.is_correct():
            return False

        already_completed = self.has_completed_question(attempt.question_id)
        if already_completed:
            return False

        self.mark_question_completed(attempt.question_id)
        if attempt.awarded_points is None:
            raise InvalidProgressError('Correct question attempt must have awarded points.')
        self.add_points(attempt.awarded_points)
        return True

    def sync_section_completion(self, section: Section) -> bool:
        if not section.is_completed_by(
                completed_question_ids=self.completed_question_ids,
                completed_task_ids=self.completed_task_ids,
                completed_code_task_ids=self.completed_code_task_ids,
        ):
            return False

        already_completed = self.has_completed_section(section.id)
        self.mark_section_completed(section.id)
        return not already_completed

    def completed_sections_count(self) -> int:
        return len(self.completed_section_ids)

    def course_completion_ratio(self, total_sections_count: int) -> float:
        if total_sections_count < 1:
            return 0.0
        return min(1.0, len(self.completed_section_ids) / total_sections_count)

    def is_course_completed(self, total_sections_count: int) -> bool:
        return total_sections_count > 0 and len(self.completed_section_ids) >= total_sections_count

    def add_points(self, points: int) -> None:
        if points < 0:
            raise InvalidProgressError('Progress points increment cannot be negative.')
        self.total_points += points

    def has_completed_module(self, module_id: UUID) -> bool:
        return module_id in self.completed_module_ids

    def mark_module_completed(self, module_id: UUID) -> None:
        if module_id not in self.completed_module_ids:
            self.completed_module_ids.append(module_id)

    def sync_module_completion(self, module: Module) -> bool:
        if not module.is_completed_by(self.completed_section_ids):
            return False

        already_completed = self.has_completed_module(module.id)
        self.mark_module_completed(module.id)
        return not already_completed

    def completed_modules_count(self) -> int:
        return len(self.completed_module_ids)

    def has_any_points(self) -> bool:
        return self.total_points > 0

    def is_empty(self) -> bool:
        return (
                not self.completed_question_ids
                and not self.completed_task_ids
                and not self.completed_code_task_ids
                and not self.completed_section_ids
                and not self.completed_module_ids
                and self.total_points == 0
        )

    def has_completed_task(self, task_id: UUID) -> bool:
        return task_id in self.completed_task_ids

    def mark_task_completed(self, task_id: UUID) -> None:
        if task_id not in self.completed_task_ids:
            self.completed_task_ids.append(task_id)

    def apply_correct_task_attempt(self, attempt: TaskAttempt) -> bool:
        if attempt.student_id != self.student_id:
            raise InvalidProgressError('Task attempt does not belong to this student.')

        if not attempt.is_correct():
            return False

        already_completed = self.has_completed_task(attempt.task_id)
        if already_completed:
            return False

        self.mark_task_completed(attempt.task_id)
        if attempt.awarded_points is None:
            raise InvalidProgressError('Correct task attempt must have awarded points.')
        self.add_points(attempt.awarded_points)
        return True

    def has_completed_code_task(self, code_task_id: UUID) -> bool:
        return code_task_id in self.completed_code_task_ids

    def mark_code_task_completed(self, code_task_id: UUID) -> None:
        if code_task_id not in self.completed_code_task_ids:
            self.completed_code_task_ids.append(code_task_id)

    def complete_code_task(self, code_task_id: UUID, reward_points: int) -> bool:
        if self.has_completed_code_task(code_task_id):
            return False

        self.mark_code_task_completed(code_task_id)
        self.add_points(reward_points)
        return True
