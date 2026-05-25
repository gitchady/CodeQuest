from uuid import uuid4

from app.domain.entities.code_submission import CodeSubmission
from app.domain.entities.test_case import TestCase as DomainTestCase
from app.infrastructure.execution.java_submission_bundle_builder import (
    JavaSubmissionBundleBuilder,
)
from app.infrastructure.execution.python_submission_bundle_builder import (
    PythonSubmissionBundleBuilder,
)


def make_submission() -> CodeSubmission:
    return CodeSubmission(
        id=uuid4(),
        code_task_id=uuid4(),
        student_id=uuid4(),
        source_code='print(1)',
        attempt_number=1,
    )


def make_hidden_test_case(submission: CodeSubmission) -> DomainTestCase:
    return DomainTestCase(
        id=uuid4(),
        code_task_id=submission.code_task_id,
        position=1,
        input_data='secret input',
        expected_output='secret expected',
        is_hidden=True,
    )


def test_python_bundle_failure_message_does_not_reveal_hidden_expected_output() -> None:
    submission = make_submission()
    temp_dir, bundle = PythonSubmissionBundleBuilder().build(
        submission,
        [make_hidden_test_case(submission)],
    )
    try:
        script = (bundle.directory / 'run.sh').read_text(encoding='utf-8')
    finally:
        temp_dir.cleanup()

    assert "expected '$normalized_expected_1'" not in script
    assert "got '$normalized_actual_1'" not in script
    assert 'echo "Test case 1 failed."' in script


def test_java_bundle_failure_message_does_not_reveal_hidden_expected_output() -> None:
    submission = make_submission()
    temp_dir, bundle = JavaSubmissionBundleBuilder().build(
        submission,
        [make_hidden_test_case(submission)],
    )
    try:
        script = (bundle.directory / 'run.sh').read_text(encoding='utf-8')
    finally:
        temp_dir.cleanup()

    assert "expected '$normalized_expected_1'" not in script
    assert "got '$normalized_actual_1'" not in script
    assert 'echo "Test case 1 failed."' in script
