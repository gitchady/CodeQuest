from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.task import Task
from app.domain.entities.task_attempt import TaskAttemptStatus


@dataclass(slots=True)
class TaskCheckResult:
    status: TaskAttemptStatus
    awarded_points: int


class TaskChecker(ABC):
    @abstractmethod
    async def check(self, task: Task, submitted_answer: str) -> TaskCheckResult:
        raise NotImplementedError