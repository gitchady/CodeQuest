from pathlib import Path
from tempfile import TemporaryDirectory

from app.domain.entities.code_submission import CodeSubmission
from app.domain.entities.test_case import TestCase
from app.infrastructure.execution.submission_bundle_builder import (
    ExecutionBundle,
    SubmissionBundleBuilder,
)


class PythonSubmissionBundleBuilder(SubmissionBundleBuilder):
    def build(
        self,
        submission: CodeSubmission,
        test_cases: list[TestCase],
    ) -> tuple[TemporaryDirectory[str], ExecutionBundle]:
        temp_dir = TemporaryDirectory()
        bundle_dir = Path(temp_dir.name)

        solution_path = bundle_dir / 'solution.py'
        run_path = bundle_dir / 'run.sh'

        solution_path.write_text(submission.source_code, encoding='utf-8')
        run_path.write_text(
            self._render_run_script(test_cases),
            encoding='utf-8',
            newline='\n',
        )
        run_path.chmod(0o755)

        return temp_dir, ExecutionBundle(
            directory=bundle_dir,
            command=['sh', 'run.sh'],
        )

    def _render_run_script(self, test_cases: list[TestCase]) -> str:
        lines = [
            '#!/bin/sh',
            'set -eu',
            '',
        ]

        for index, test_case in enumerate(test_cases, start=1):
            escaped_input = self._escape_shell_string(test_case.input_data)
            escaped_expected = self._escape_shell_string(test_case.expected_output)

            lines.extend([
                f"actual_output_{index}=$(printf '%s' '{escaped_input}' | python solution.py | tr -d '\\r')",
                f"expected_output_{index}=$(printf '%s' '{escaped_expected}' | tr -d '\\r')",
                f"normalized_actual_{index}=$(printf '%s' \"$actual_output_{index}\" | sed 's/[[:space:]]*$//')",
                f"normalized_expected_{index}=$(printf '%s' \"$expected_output_{index}\" | sed 's/[[:space:]]*$//')",
                f"if [ \"$normalized_actual_{index}\" != \"$normalized_expected_{index}\" ]; then",
                self._render_failure_message(index, test_case),
                '  exit 1',
                'fi',
                '',
            ])

        return '\n'.join(lines)

    def _escape_shell_string(self, value: str) -> str:
        return value.replace("'", "'\"'\"'")

    def _render_failure_message(self, index: int, test_case: TestCase) -> str:
        if test_case.is_hidden:
            return f'  echo "Test case {index} failed." >&2'
        return (
            f"  echo \"Test case {index} failed: "
            f"expected '$normalized_expected_{index}', "
            f"got '$normalized_actual_{index}'\" >&2"
        )
