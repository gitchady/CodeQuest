from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import QuestionAlreadyUsedError, QuestionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class DeleteQuestionCommand:
    actor: User
    question_id: UUID


class DeleteQuestionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteQuestionCommand) -> None:
        async with self.uow:
            question = await self.uow.questions.get_by_id(command.question_id)
            if question is None:
                raise QuestionNotFoundError('Question not found.')

            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=question.section_id,
            )

            has_attempts = await self.uow.question_attempts.exists_by_question_id(question.id)
            if has_attempts:
                raise QuestionAlreadyUsedError(
                    'Question already has student attempts and cannot be changed safely.'
                )

            section.remove_question(question.id)
            await self.uow.sections.update(section)
            await self.uow.questions.remove(question.id)
            await self.uow.commit()
