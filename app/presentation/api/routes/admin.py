from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.application.use_cases.courses.create_course import (
    CreateCourseCommand,
    CreateCourseUseCase,
)
from app.application.use_cases.courses.delete_course import (
    DeleteCourseCommand,
    DeleteCourseUseCase,
)
from app.application.use_cases.courses.update_course import (
    UpdateCourseCommand,
    UpdateCourseUseCase,
)
from app.application.use_cases.lectures.create_lecture import (
    CreateLectureCommand,
    CreateLectureUseCase,
)
from app.application.use_cases.lectures.delete_lecture import (
    DeleteLectureCommand,
    DeleteLectureUseCase,
)
from app.application.use_cases.lectures.update_lecture import (
    UpdateLectureCommand,
    UpdateLectureUseCase,
)
from app.application.use_cases.modules.create_module import (
    CreateModuleCommand,
    CreateModuleUseCase,
)
from app.application.use_cases.modules.delete_module import (
    DeleteModuleCommand,
    DeleteModuleUseCase,
)
from app.application.use_cases.modules.update_module import (
    UpdateModuleCommand,
    UpdateModuleUseCase,
)
from app.application.use_cases.sections.create_section import (
    CreateSectionCommand,
    CreateSectionUseCase,
)
from app.application.use_cases.sections.delete_section import (
    DeleteSectionCommand,
    DeleteSectionUseCase,
)
from app.application.use_cases.sections.update_section import (
    UpdateSectionCommand,
    UpdateSectionUseCase,
)
from app.domain.entities.user import User
from app.presentation.api.dependencies import (
    get_create_course_use_case,
    get_create_lecture_use_case,
    get_create_module_use_case,
    get_create_section_use_case,
    get_current_author_or_admin,
    get_delete_course_use_case,
    get_delete_lecture_use_case,
    get_delete_module_use_case,
    get_delete_section_use_case,
    get_update_course_use_case,
    get_update_lecture_use_case,
    get_update_module_use_case,
    get_update_section_use_case,
)
from app.presentation.api.schemas import (
    CourseResponse,
    CreateCourseRequest,
    CreateLectureRequest,
    CreateModuleRequest,
    CreateSectionRequest,
    ErrorResponse,
    LectureResponse,
    ModuleResponse,
    SectionResponse,
    UpdateCourseRequest,
    UpdateLectureRequest,
    UpdateModuleRequest,
    UpdateSectionRequest,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={
        401: {
            "description": "Authentication credentials are missing or invalid.",
            "model": ErrorResponse,
        },
        403: {
            "description": "Author or admin access is required.",
            "model": ErrorResponse,
        },
    },
)


@router.post(
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create course",
    description="Creates a new course owned by the current author or administrator.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
    },
)
async def create_course(
        request: CreateCourseRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: CreateCourseUseCase = Depends(get_create_course_use_case),
) -> CourseResponse:
    result = await use_case.execute(
        CreateCourseCommand(
            actor=actor,
            title=request.title,
            description=request.description,
        )
    )
    return CourseResponse.model_validate(result)


@router.put(
    "/courses/{course_id}",
    response_model=CourseResponse,
    summary="Update course",
    description="Updates a course if the current user owns it or manages the platform.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_course(
        course_id: UUID,
        request: UpdateCourseRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: UpdateCourseUseCase = Depends(get_update_course_use_case),
) -> CourseResponse:
    result = await use_case.execute(
        UpdateCourseCommand(
            actor=actor,
            course_id=course_id,
            title=request.title,
            description=request.description,
        )
    )
    return CourseResponse.model_validate(result)


@router.delete(
    "/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete course",
    description="Deletes a course together with its entire content subtree.",
    responses={
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_course(
        course_id: UUID,
        actor: User = Depends(get_current_author_or_admin),
        use_case: DeleteCourseUseCase = Depends(get_delete_course_use_case),
) -> Response:
    await use_case.execute(
        DeleteCourseCommand(
            actor=actor,
            course_id=course_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/courses/{course_id}/modules",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create module",
    description="Creates a new module inside a course available to the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Course was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_module(
        course_id: UUID,
        request: CreateModuleRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: CreateModuleUseCase = Depends(get_create_module_use_case),
) -> ModuleResponse:
    result = await use_case.execute(
        CreateModuleCommand(
            actor=actor,
            course_id=course_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return ModuleResponse.model_validate(result)


@router.put(
    "/modules/{module_id}",
    response_model=ModuleResponse,
    summary="Update module",
    description="Updates a module if it belongs to a course managed by the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_module(
        module_id: UUID,
        request: UpdateModuleRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: UpdateModuleUseCase = Depends(get_update_module_use_case),
) -> ModuleResponse:
    result = await use_case.execute(
        UpdateModuleCommand(
            actor=actor,
            module_id=module_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return ModuleResponse.model_validate(result)


@router.delete(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete module",
    description="Deletes a module together with its nested sections and lectures.",
    responses={
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_module(
        module_id: UUID,
        actor: User = Depends(get_current_author_or_admin),
        use_case: DeleteModuleUseCase = Depends(get_delete_module_use_case),
) -> Response:
    await use_case.execute(
        DeleteModuleCommand(
            actor=actor,
            module_id=module_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/modules/{module_id}/sections",
    response_model=SectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create section",
    description="Creates a new section inside a module managed by the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Module was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_section(
        module_id: UUID,
        request: CreateSectionRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: CreateSectionUseCase = Depends(get_create_section_use_case),
) -> SectionResponse:
    result = await use_case.execute(
        CreateSectionCommand(
            actor=actor,
            module_id=module_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return SectionResponse.model_validate(result)


@router.put(
    "/sections/{section_id}",
    response_model=SectionResponse,
    summary="Update section",
    description="Updates a section if it belongs to a course managed by the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_section(
        section_id: UUID,
        request: UpdateSectionRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: UpdateSectionUseCase = Depends(get_update_section_use_case),
) -> SectionResponse:
    result = await use_case.execute(
        UpdateSectionCommand(
            actor=actor,
            section_id=section_id,
            title=request.title,
            description=request.description,
            position=request.position,
        )
    )
    return SectionResponse.model_validate(result)


@router.delete(
    "/sections/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete section",
    description="Deletes a section together with all nested lectures and activities.",
    responses={
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_section(
        section_id: UUID,
        actor: User = Depends(get_current_author_or_admin),
        use_case: DeleteSectionUseCase = Depends(get_delete_section_use_case),
) -> Response:
    await use_case.execute(
        DeleteSectionCommand(
            actor=actor,
            section_id=section_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sections/{section_id}/lectures",
    response_model=LectureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lecture",
    description="Creates a lecture inside a section available to the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Section was not found.",
            "model": ErrorResponse,
        },
    },
)
async def create_lecture(
        section_id: UUID,
        request: CreateLectureRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: CreateLectureUseCase = Depends(get_create_lecture_use_case),
) -> LectureResponse:
    result = await use_case.execute(
        CreateLectureCommand(
            actor=actor,
            section_id=section_id,
            title=request.title,
            content=request.content,
            position=request.position,
        )
    )
    return LectureResponse.model_validate(result)


@router.put(
    "/lectures/{lecture_id}",
    response_model=LectureResponse,
    summary="Update lecture",
    description="Updates a lecture if it belongs to a course managed by the current user.",
    responses={
        400: {
            "description": "Domain or application validation error.",
            "model": ErrorResponse,
        },
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_lecture(
        lecture_id: UUID,
        request: UpdateLectureRequest,
        actor: User = Depends(get_current_author_or_admin),
        use_case: UpdateLectureUseCase = Depends(get_update_lecture_use_case),
) -> LectureResponse:
    result = await use_case.execute(
        UpdateLectureCommand(
            actor=actor,
            lecture_id=lecture_id,
            title=request.title,
            content=request.content,
            position=request.position,
        )
    )
    return LectureResponse.model_validate(result)


@router.delete(
    "/lectures/{lecture_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lecture",
    description="Deletes a lecture from a course managed by the current user.",
    responses={
        404: {
            "description": "Lecture was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_lecture(
        lecture_id: UUID,
        actor: User = Depends(get_current_author_or_admin),
        use_case: DeleteLectureUseCase = Depends(get_delete_lecture_use_case),
) -> Response:
    await use_case.execute(
        DeleteLectureCommand(
            actor=actor,
            lecture_id=lecture_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)