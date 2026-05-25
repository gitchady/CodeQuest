from dataclasses import dataclass
from uuid import UUID

from app.application.dto.question_attempt import QuestionAttemptResultDTO
from app.application.exceptions import QuestionAttemptNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class GetQuestionAttemptResultCommand:
    actor: User
    attempt_id: UUID


class GetQuestionAttemptResultUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(
        self,
        command: GetQuestionAttemptResultCommand,
    ) -> QuestionAttemptResultDTO:
        async with self.uow:
            attempt = await self.uow.question_attempts.get_by_id(command.attempt_id)
            if attempt is None:
                raise QuestionAttemptNotFoundError('Question attempt not found.')

            if attempt.student_id != command.actor.id:
                await self.course_access_service.ensure_can_view_question_results(
                    actor=command.actor,
                    question_id=attempt.question_id,
                )

            if (
                attempt.result_status is None
                or attempt.awarded_points is None
                or attempt.checked_at is None
            ):
                raise QuestionAttemptNotFoundError('Question attempt result not found.')

            return QuestionAttemptResultDTO(
                attempt_id=attempt.id,
                question_id=attempt.question_id,
                attempt_number=attempt.attempt_number,
                result_status=attempt.result_status,
                awarded_points=attempt.awarded_points,
                checked_at=attempt.checked_at,
                selected_option_ids=list(attempt.selected_option_ids),
            )
