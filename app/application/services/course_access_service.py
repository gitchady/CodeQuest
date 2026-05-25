from uuid import UUID

from app.application.exceptions import (
    CourseNotFoundError,
    ModuleNotFoundError,
    PermissionDeniedError,
    SectionNotFoundError, QuestionNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities import Question
from app.domain.entities.course import Course
from app.domain.entities.module import Module
from app.domain.entities.section import Section
from app.domain.entities.user import User


class CourseAccessService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def ensure_can_manage_course(
            self,
            actor: User,
            course_id: UUID,
    ) -> Course:
        course = await self.uow.courses.get_by_id(course_id)
        if course is None:
            raise CourseNotFoundError('Course not found.')

        if not actor.can_manage_platform() and not course.is_owned_by(actor.id):
            raise PermissionDeniedError('User cannot manage this course.')

        return course

    async def ensure_can_manage_module(
            self,
            actor: User,
            module_id: UUID,
    ) -> Module:
        module = await self.uow.modules.get_by_id(module_id)
        if module is None:
            raise ModuleNotFoundError('Module not found.')

        await self.ensure_can_manage_course(actor, module.course_id)
        return module

    async def ensure_can_manage_section(
            self,
            actor: User,
            section_id: UUID,
    ) -> Section:
        section = await self.uow.sections.get_by_id(section_id)
        if section is None:
            raise SectionNotFoundError('Section not found.')

        await self.ensure_can_manage_module(actor, section.module_id)
        return section

    async def ensure_can_view_question_results(
            self,
            actor: User,
            question_id: UUID,
    ) -> Question:
        question = await self.uow.questions.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundError('Question not found.')

        section = await self.uow.sections.get_by_id(question.section_id)
        if section is None:
            raise SectionNotFoundError('Section not found.')

        module = await self.uow.modules.get_by_id(section.module_id)
        if module is None:
            raise ModuleNotFoundError('Module not found.')

        course = await self.uow.courses.get_by_id(module.course_id)
        if course is None:
            raise CourseNotFoundError('Course not found.')

        if actor.is_admin():
            return question

        if actor.is_author() and course.is_owned_by(actor.id):
            return question

        raise PermissionDeniedError('User cannot view question results.')
