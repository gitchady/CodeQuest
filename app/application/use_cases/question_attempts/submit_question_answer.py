from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.exceptions import (
    ModuleNotFoundError,
    PermissionDeniedError,
    QuestionNotFoundError,
    SectionNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.progress import Progress
from app.domain.entities.question_attempt import QuestionAttempt
from app.domain.entities.user import User


@dataclass(slots=True)
class SubmitQuestionAnswerCommand:
    actor: User
    question_id: UUID
    selected_option_ids: list[UUID]


class SubmitQuestionAnswerUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: SubmitQuestionAnswerCommand) -> QuestionAttempt:
        if not command.actor.can_take_learning_activities():
            raise PermissionDeniedError('User cannot submit question answers.')

        async with self.uow:
            question = await self.uow.questions.get_by_id(command.question_id)
            if question is None:
                raise QuestionNotFoundError('Question not found.')

            answer_options = await self.uow.answer_options.get_by_ids(question.answer_option_ids)
            question.validate_answer_options_configuration(answer_options)

            attempts = await self.uow.question_attempts.get_by_student_and_question(
                student_id=command.actor.id,
                question_id=question.id,
            )
            has_correct_attempt = any(attempt.is_correct() for attempt in attempts)

            question.ensure_attempt_available(
                existing_attempts_count=len(attempts),
                has_correct_attempt=has_correct_attempt,
            )

            attempt = QuestionAttempt(
                id=uuid4(),
                question_id=question.id,
                student_id=command.actor.id,
                attempt_number=len(attempts) + 1,
                selected_option_ids=command.selected_option_ids,
            )

            result_status = question.resolve_result_status(
                selected_option_ids=attempt.selected_option_ids,
                answer_options=answer_options,
            )
            awarded_points = question.resolve_awarded_points(
                selected_option_ids=attempt.selected_option_ids,
                answer_options=answer_options,
            )

            attempt.apply_result(
                result_status=result_status,
                awarded_points=awarded_points,
            )

            await self.uow.question_attempts.add(attempt)

            if attempt.is_correct():
                section = await self.uow.sections.get_by_id(question.section_id)
                if section is None:
                    raise SectionNotFoundError('Section not found.')

                module = await self.uow.modules.get_by_id(section.module_id)
                if module is None:
                    raise ModuleNotFoundError('Module not found.')

                progress = await self.uow.progress.get_by_student_and_course(
                    student_id=command.actor.id,
                    course_id=module.course_id,
                )

                progress_is_new = progress is None
                if progress is None:
                    progress = Progress(
                        id=uuid4(),
                        student_id=command.actor.id,
                        course_id=module.course_id,
                    )

                progress_changed = progress.apply_correct_attempt(attempt)
                if progress_changed:
                    progress.sync_section_completion(section)
                    progress.sync_module_completion(module)

                    if progress_is_new:
                        await self.uow.progress.add(progress)
                    else:
                        await self.uow.progress.update(progress)

            await self.uow.commit()
            return attempt