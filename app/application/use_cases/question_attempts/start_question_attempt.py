from dataclasses import dataclass
from uuid import UUID

from app.application.dto.question_attempt import (
    QuestionAttemptAnswerOptionDTO,
    StartQuestionAttemptDTO,
)
from app.application.exceptions import PermissionDeniedError, QuestionNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.user import User


@dataclass(slots=True)
class StartQuestionAttemptCommand:
    actor: User
    question_id: UUID


class StartQuestionAttemptUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: StartQuestionAttemptCommand) -> StartQuestionAttemptDTO:
        if not command.actor.can_take_learning_activities():
            raise PermissionDeniedError('User cannot start question attempts.')

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
            last_attempt = attempts[-1] if attempts else None
            has_correct_attempt = any(attempt.is_correct() for attempt in attempts)

            can_submit = question.can_start_attempt(
                existing_attempts_count=len(attempts),
                has_correct_attempt=has_correct_attempt,
            )

            return StartQuestionAttemptDTO(
                question_id=question.id,
                text=question.text,
                question_type=question.question_type,
                attempt_number=len(attempts) + 1,
                max_attempts=question.max_attempts,
                reward_points=question.reward_points,
                can_submit=can_submit,
                is_solved=has_correct_attempt,
                attempts_used=len(attempts),
                selected_option_ids=list(last_attempt.selected_option_ids) if last_attempt else [],
                last_result_status=last_attempt.result_status if last_attempt else None,
                last_awarded_points=last_attempt.awarded_points if last_attempt else None,
                answer_options=[
                    QuestionAttemptAnswerOptionDTO(
                        id=option.id,
                        text=option.text,
                        position=option.position,
                    )
                    for option in sorted(answer_options, key=lambda item: item.position)
                ],
            )
