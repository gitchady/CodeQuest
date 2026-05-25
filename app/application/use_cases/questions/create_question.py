from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.user import User


@dataclass(slots=True)
class CreateQuestionCommand:
    actor: User
    section_id: UUID
    text: str
    position: int
    question_type: QuestionType
    max_attempts: int
    reward_points: int


class CreateQuestionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: CreateQuestionCommand) -> Question:
        async with self.uow:
            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=command.section_id,
            )

            question = Question(
                id=uuid4(),
                section_id=command.section_id,
                text=command.text,
                position=command.position,
                question_type=command.question_type,
                max_attempts=command.max_attempts,
                reward_points=command.reward_points,
            )
            section.add_question(question.id)
            await self.uow.questions.add(question)
            await self.uow.sections.update(section)
            await self.uow.commit()
            return question