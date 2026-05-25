from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    AnswerOptionNotFoundError,
    QuestionAlreadyUsedError,
    QuestionNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.answer_option import AnswerOption
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateAnswerOptionCommand:
    actor: User
    answer_option_id: UUID
    text: str
    position: int
    is_correct: bool


class UpdateAnswerOptionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateAnswerOptionCommand) -> AnswerOption:
        async with self.uow:
            answer_option = await self.uow.answer_options.get_by_id(command.answer_option_id)
            if answer_option is None:
                raise AnswerOptionNotFoundError('Answer option not found.')

            question = await self.uow.questions.get_by_id(answer_option.question_id)
            if question is None:
                raise QuestionNotFoundError('Question not found.')

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=question.section_id,
            )

            has_attempts = await self.uow.question_attempts.exists_by_question_id(
                answer_option.question_id
            )
            if has_attempts:
                raise QuestionAlreadyUsedError(
                    'Question already has student attempts and cannot be changed safely.'
                )

            answer_option.update(
                text=command.text,
                position=command.position,
                is_correct=command.is_correct,
            )
            await self.uow.answer_options.update(answer_option)
            await self.uow.commit()
            return answer_option
