from uuid import UUID

from app.domain.entities.code_submission import CodeSubmission, CodeSubmissionStatus
from app.infrastructure.database.models.code_submission_model import CodeSubmissionModel


class CodeSubmissionMapper:
    @staticmethod
    def to_domain(model: CodeSubmissionModel) -> CodeSubmission:
        return CodeSubmission(
            id=UUID(model.id),
            code_task_id=UUID(model.code_task_id),
            student_id=UUID(model.student_id),
            source_code=model.source_code,
            attempt_number=model.attempt_number,
            status=CodeSubmissionStatus(model.status),
            created_at=model.created_at,
            started_at=model.started_at,
            finished_at=model.finished_at,
        )

    @staticmethod
    def to_model(entity: CodeSubmission) -> CodeSubmissionModel:
        return CodeSubmissionModel(
            id=str(entity.id),
            code_task_id=str(entity.code_task_id),
            student_id=str(entity.student_id),
            source_code=entity.source_code,
            attempt_number=entity.attempt_number,
            status=str(entity.status),
            created_at=entity.created_at,
            started_at=entity.started_at,
            finished_at=entity.finished_at,
        )