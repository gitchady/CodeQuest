from uuid import uuid4

from app.domain.entities.module import Module
from app.domain.entities.progress import Progress
from app.domain.entities.question_attempt import QuestionAttempt, QuestionResultStatus
from app.domain.entities.section import Section


def test_progress_applies_correct_attempt_only_once() -> None:
    student_id = uuid4()
    question_id = uuid4()
    progress = Progress(id=uuid4(), student_id=student_id, course_id=uuid4())
    attempt = QuestionAttempt(
        id=uuid4(),
        question_id=question_id,
        student_id=student_id,
        attempt_number=1,
        selected_option_ids=[uuid4()],
    )
    attempt.apply_result(QuestionResultStatus.CORRECT, 5)

    assert progress.apply_correct_attempt(attempt) is True
    assert progress.apply_correct_attempt(attempt) is False
    assert progress.completed_question_ids == [question_id]
    assert progress.total_points == 5


def test_progress_syncs_section_and_module_completion() -> None:
    question_id = uuid4()
    section = Section(
        id=uuid4(),
        module_id=uuid4(),
        title='HTTP',
        description='Methods',
        position=1,
        question_ids=[question_id],
    )
    module = Module(
        id=uuid4(),
        course_id=uuid4(),
        title='Basics',
        description='Base module',
        position=1,
        section_ids=[section.id],
    )
    progress = Progress(
        id=uuid4(),
        student_id=uuid4(),
        course_id=module.course_id,
        completed_question_ids=[question_id],
    )

    assert progress.sync_section_completion(section) is True
    assert progress.sync_module_completion(module) is True
    assert progress.completed_section_ids == [section.id]
    assert progress.completed_module_ids == [module.id]
