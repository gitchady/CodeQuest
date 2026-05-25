from dataclasses import dataclass
from uuid import UUID

from app.application.dto.course_structure import (
    CodeTaskStructureDTO,
    CourseStructureDTO,
    LectureStructureDTO,
    ModuleStructureDTO,
    SectionStructureDTO,
    TaskStructureDTO,
)
from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.repositories.code_task_repository import CodeTaskRepository
from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.interfaces.repositories.lecture_repository import LectureRepository
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.section_repository import SectionRepository
from app.application.interfaces.repositories.task_repository import TaskRepository


@dataclass(slots=True)
class GetCourseStructureQuery:
    course_id: UUID


class GetCourseStructureUseCase:
    def __init__(
        self,
        course_repository: CourseRepository,
        module_repository: ModuleRepository,
        section_repository: SectionRepository,
        lecture_repository: LectureRepository,
        task_repository: TaskRepository,
        code_task_repository: CodeTaskRepository,
    ) -> None:
        self.course_repository = course_repository
        self.module_repository = module_repository
        self.section_repository = section_repository
        self.lecture_repository = lecture_repository
        self.task_repository = task_repository
        self.code_task_repository = code_task_repository

    async def execute(self, query: GetCourseStructureQuery) -> CourseStructureDTO | None:
        course = await self.course_repository.get_by_id(query.course_id)
        if course is None:
            raise CourseNotFoundError("Course not found.")

        modules = await self.module_repository.get_by_ids(course.module_ids)
        all_section_ids = [
            section_id
            for module in modules
            for section_id in module.section_ids
        ]
        sections = await self.section_repository.get_by_ids(all_section_ids)
        all_lecture_ids = [
            lecture_id
            for section in sections
            for lecture_id in section.lecture_ids
        ]
        all_task_ids = [
            task_id
            for section in sections
            for task_id in section.task_ids
        ]
        all_code_task_ids = [
            code_task_id
            for section in sections
            for code_task_id in section.code_task_ids
        ]
        lectures = await self.lecture_repository.get_by_ids(all_lecture_ids)
        tasks = await self.task_repository.get_by_ids(all_task_ids)
        code_tasks = await self.code_task_repository.get_by_ids(all_code_task_ids)

        sections_by_id = {section.id: section for section in sections}
        lectures_by_id = {lecture.id: lecture for lecture in lectures}
        tasks_by_id = {task.id: task for task in tasks}
        code_tasks_by_id = {code_task.id: code_task for code_task in code_tasks}
        module_dtos: list[ModuleStructureDTO] = []

        for module in sorted(modules, key=lambda item: item.position):
            module_sections = [
                sections_by_id[section_id]
                for section_id in module.section_ids
                if section_id in sections_by_id
            ]
            section_dtos: list[SectionStructureDTO] = []

            for section in sorted(module_sections, key=lambda item: item.position):
                section_tasks = [
                    tasks_by_id[task_id]
                    for task_id in section.task_ids
                    if task_id in tasks_by_id
                ]
                section_code_tasks = [
                    code_tasks_by_id[code_task_id]
                    for code_task_id in section.code_task_ids
                    if code_task_id in code_tasks_by_id
                ]
                section_lectures = [
                    lectures_by_id[lecture_id]
                    for lecture_id in section.lecture_ids
                    if lecture_id in lectures_by_id
                ]
                task_dtos = [
                    TaskStructureDTO(
                        id=task.id,
                        title=task.title,
                        position=task.position,
                    )
                    for task in sorted(section_tasks, key=lambda item: item.position)
                ]

                code_task_dtos = [
                    CodeTaskStructureDTO(
                        id=code_task.id,
                        title=code_task.title,
                        position=code_task.position,
                        language=str(code_task.language),
                    )
                    for code_task in sorted(section_code_tasks, key=lambda item: item.position)
                ]
                lecture_dtos = [
                    LectureStructureDTO(
                        id=lecture.id,
                        title=lecture.title,
                        position=lecture.position,
                    )
                    for lecture in sorted(section_lectures, key=lambda item: item.position)
                ]
                section_dtos.append(
                    SectionStructureDTO(
                        id=section.id,
                        title=section.title,
                        description=section.description,
                        position=section.position,
                        question_ids=list(section.question_ids),
                        task_ids=list(section.task_ids),
                        code_task_ids=list(section.code_task_ids),
                        tasks=task_dtos,
                        code_tasks=code_task_dtos,
                        lectures=lecture_dtos,
                    )
                )

            module_dtos.append(
                ModuleStructureDTO(
                    id=module.id,
                    title=module.title,
                    description=module.description,
                    position=module.position,
                    sections=section_dtos,
                )
            )

        return CourseStructureDTO(
            id=course.id,
            title=course.title,
            description=course.description,
            modules=module_dtos,
        )
