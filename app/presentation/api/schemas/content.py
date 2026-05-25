from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.entities.question import QuestionType


class CourseBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str


class CourseListItemResponse(CourseBaseResponse):
    pass


class CourseResponse(CourseBaseResponse):
    pass



class LectureBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    position: int


class LectureResponse(LectureBaseResponse):
    content: str
    section_id: UUID


class LectureStructureResponse(LectureBaseResponse):
    pass



class SectionBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    position: int


class TaskStructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    position: int


class CodeTaskStructureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    position: int
    language: str

class SectionStructureResponse(SectionBaseResponse):
    question_ids: list[UUID]
    task_ids: list[UUID]
    code_task_ids: list[UUID]
    tasks: list[TaskStructureResponse]
    code_tasks: list[CodeTaskStructureResponse]
    lectures: list[LectureStructureResponse]



class ModuleBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    position: int



class ModuleStructureResponse(ModuleBaseResponse):
    sections: list[SectionStructureResponse]


class CourseStructureResponse(CourseBaseResponse):
    modules: list[ModuleStructureResponse]


class AnswerOptionDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    position: int


class QuestionDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    section_id: UUID
    text: str
    position: int
    question_type: QuestionType
    max_attempts: int
    reward_points: int
    answer_options: list[AnswerOptionDetailsResponse]


class TaskDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    section_id: UUID
    title: str
    statement: str
    position: int
    max_attempts: int
    reward_points: int


class CodeTaskDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    section_id: UUID
    title: str
    statement: str
    position: int
    language: str
    starter_code: str
    max_attempts: int
    reward_points: int
    time_limit_seconds: int
    memory_limit_mb: int
