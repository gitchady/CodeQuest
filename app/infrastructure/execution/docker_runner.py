import asyncio
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.application.exceptions import RetryableExecutionError

@dataclass(slots=True)
class DockerRunResult:
    stdout: str
    stderr: str
    exit_code: int | None
    logs: str = ''

@dataclass(slots=True)
class DockerRunConfig:
    container_workdir: str = '/workspace'
    cpus: str = '1'
    tmpfs_size_mb: int = 64
    pids_limit: int = 64
    output_limit_bytes: int = 64 * 1024


DOCKER_INFRASTRUCTURE_ERROR_MARKERS = (
    'cannot connect to the docker daemon',
    'failed to connect to the docker api',
    'docker daemon is not running',
)


class DockerRunner:
    def __init__(self, config: DockerRunConfig) -> None:
        self.config = config

    async def run(
        self,
        image: str,
        bundle_dir: Path,
        command: list[str],
        time_limit_seconds: int,
        memory_limit_mb: int,
    ) -> DockerRunResult:
        self._make_bundle_readable(bundle_dir)
        container_name = f'code-submission-{uuid4().hex}'
        docker_command = [
            'docker',
            'run',
            '--name',
            container_name,
            '--rm',
            '--network',
            'none',
            '--read-only',
            '--tmpfs',
            f'/tmp:size={self.config.tmpfs_size_mb}m',
            '--cap-drop',
            'ALL',
            '--security-opt',
            'no-new-privileges',
            '--pids-limit',
            str(self.config.pids_limit),
            '--memory',
            f'{memory_limit_mb}m',
            '--cpus',
            self.config.cpus,
            '-v',
            f'{bundle_dir}:{self.config.container_workdir}:ro',
            '-w',
            self.config.container_workdir,
            image,
            *command,
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *docker_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise RetryableExecutionError('Docker executable not found.') from exc
        except OSError as exc:
            raise RetryableExecutionError('Docker process could not be started.') from exc

        stdout_task = asyncio.create_task(self._read_limited(process.stdout))
        stderr_task = asyncio.create_task(self._read_limited(process.stderr))

        try:
            await asyncio.wait_for(
                process.wait(),
                timeout=time_limit_seconds,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            await self._remove_container(container_name)
            await asyncio.gather(stdout_task, stderr_task)
            return DockerRunResult(
                stdout='',
                stderr='Execution timed out.',
                exit_code=None,
                logs='Docker container killed by timeout.',
            )

        (stdout_bytes, stdout_truncated), (stderr_bytes, stderr_truncated) = (
            await asyncio.gather(stdout_task, stderr_task)
        )
        stderr = stderr_bytes.decode('utf-8', errors='replace')
        if process.returncode != 0 and self._is_docker_infrastructure_error(stderr):
            raise RetryableExecutionError(stderr.strip() or 'Docker infrastructure error.')

        logs = self._build_logs(
            stdout_truncated=stdout_truncated,
            stderr_truncated=stderr_truncated,
        )
        return DockerRunResult(
            stdout=stdout_bytes.decode('utf-8', errors='replace'),
            stderr=stderr,
            exit_code=process.returncode,
            logs=logs,
        )

    def _make_bundle_readable(self, bundle_dir: Path) -> None:
        for path in (bundle_dir, *bundle_dir.rglob('*')):
            try:
                path.chmod(0o755 if path.is_dir() else 0o644)
            except OSError:
                continue

    def _is_docker_infrastructure_error(self, stderr: str) -> bool:
        normalized_stderr = stderr.lower()
        return any(
            marker in normalized_stderr
            for marker in DOCKER_INFRASTRUCTURE_ERROR_MARKERS
        )

    async def _read_limited(
        self,
        stream: asyncio.StreamReader | None,
    ) -> tuple[bytes, bool]:
        if stream is None:
            return b'', False

        chunks: list[bytes] = []
        captured_size = 0
        truncated = False

        while True:
            chunk = await stream.read(8192)
            if not chunk:
                break

            remaining = self.config.output_limit_bytes - captured_size
            if remaining > 0:
                captured = chunk[:remaining]
                chunks.append(captured)
                captured_size += len(captured)
                if len(chunk) > remaining:
                    truncated = True
            else:
                truncated = True

        return b''.join(chunks), truncated

    async def _remove_container(self, container_name: str) -> None:
        try:
            process = await asyncio.create_subprocess_exec(
                'docker',
                'rm',
                '-f',
                container_name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(process.wait(), timeout=10)
        except (FileNotFoundError, OSError, asyncio.TimeoutError):
            return

    def _build_logs(self, stdout_truncated: bool, stderr_truncated: bool) -> str:
        messages = []
        if stdout_truncated:
            messages.append('stdout truncated')
        if stderr_truncated:
            messages.append('stderr truncated')
        return '; '.join(messages)
