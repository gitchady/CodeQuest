from uuid import UUID

from app.domain.entities.progress import Progress
from app.infrastructure.database.models.progress_model import ProgressModel


class ProgressMapper:
    @staticmethod
    def to_domain(model: ProgressModel) -> Progress:
        return Progress(
            id=UUID(model.id),
            student_id=UUID(model.student_id),
            course_id=UUID(model.course_id),
            completed_code_task_ids=[UUID(item) for item in model.completed_code_task_ids],
            completed_question_ids=[UUID(item) for item in model.completed_question_ids],
            completed_task_ids=[UUID(item) for item in model.completed_task_ids],
            completed_section_ids=[UUID(item) for item in model.completed_section_ids],
            completed_module_ids=[UUID(item) for item in model.completed_module_ids],
            total_points=model.total_points,
        )

    @staticmethod
    def to_model(entity: Progress) -> ProgressModel:
        return ProgressModel(
            id=str(entity.id),
            student_id=str(entity.student_id),
            course_id=str(entity.course_id),
            completed_code_task_ids=[str(item) for item in entity.completed_code_task_ids],
            completed_question_ids=[str(item) for item in entity.completed_question_ids],
            completed_task_ids=[str(item) for item in entity.completed_task_ids],
            completed_section_ids=[str(item) for item in entity.completed_section_ids],
            completed_module_ids=[str(item) for item in entity.completed_module_ids],
            total_points=entity.total_points,
        )