from app.application.interfaces.services.task_checker import TaskCheckResult, TaskChecker
from app.domain.entities.task import Task
from app.domain.entities.task_attempt import TaskAttemptStatus


class SimpleTaskChecker(TaskChecker):
    async def check(self, task: Task, submitted_answer: str) -> TaskCheckResult:
        is_correct = task.is_correct_answer(submitted_answer)
        return TaskCheckResult(
            status=(
                TaskAttemptStatus.CORRECT
                if is_correct
                else TaskAttemptStatus.INCORRECT
            ),
            awarded_points=task.reward_points if is_correct else 0,
        )