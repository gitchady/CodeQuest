from uuid import UUID

from app.domain.entities.code_task import CodeTask, CodeTaskLanguage
from app.infrastructure.database.models.code_task_model import CodeTaskModel


class CodeTaskMapper:
    @staticmethod
    def to_domain(model: CodeTaskModel) -> CodeTask:
        return CodeTask(
            id=UUID(model.id),
            section_id=UUID(model.section_id),
            title=model.title,
            statement=model.statement,
            position=model.position,
            language=CodeTaskLanguage(model.language),
            starter_code=model.starter_code,
            max_attempts=model.max_attempts,
            reward_points=model.reward_points,
            time_limit_seconds=model.time_limit_seconds,
            memory_limit_mb=model.memory_limit_mb,
        )

    @staticmethod
    def to_model(entity: CodeTask) -> CodeTaskModel:
        return CodeTaskModel(
            id=str(entity.id),
            section_id=str(entity.section_id),
            title=entity.title,
            statement=entity.statement,
            position=entity.position,
            language=str(entity.language),
            starter_code=entity.starter_code,
            max_attempts=entity.max_attempts,
            reward_points=entity.reward_points,
            time_limit_seconds=entity.time_limit_seconds,
            memory_limit_mb=entity.memory_limit_mb,
        )