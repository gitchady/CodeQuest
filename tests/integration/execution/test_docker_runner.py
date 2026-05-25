import subprocess

import pytest

from app.infrastructure.execution.docker_runner import DockerRunConfig, DockerRunner


def docker_is_available() -> bool:
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def running_container_ids() -> set[str]:
    result = subprocess.run(
        ['docker', 'ps', '--format', '{{.ID}}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return set(result.stdout.splitlines())


@pytest.mark.asyncio
async def test_docker_runner_removes_container_after_timeout(tmp_path) -> None:
    if not docker_is_available():
        pytest.skip('Docker daemon is not available.')

    run_path = tmp_path / 'run.sh'
    run_path.write_text(
        '#!/bin/sh\npython -c "while True: pass"\n',
        encoding='utf-8',
        newline='\n',
    )
    before = running_container_ids()

    result = await DockerRunner(DockerRunConfig()).run(
        image='python:3.12-alpine',
        bundle_dir=tmp_path,
        command=['sh', 'run.sh'],
        time_limit_seconds=1,
        memory_limit_mb=128,
    )

    leaked = running_container_ids() - before
    for container_id in leaked:
        subprocess.run(['docker', 'rm', '-f', container_id], capture_output=True)

    assert result.exit_code is None
    assert leaked == set()


@pytest.mark.asyncio
async def test_docker_runner_limits_captured_output(tmp_path) -> None:
    if not docker_is_available():
        pytest.skip('Docker daemon is not available.')

    run_path = tmp_path / 'run.sh'
    run_path.write_text(
        '#!/bin/sh\npython -c "print(\'x\' * 200)"\n',
        encoding='utf-8',
        newline='\n',
    )

    result = await DockerRunner(DockerRunConfig(output_limit_bytes=32)).run(
        image='python:3.12-alpine',
        bundle_dir=tmp_path,
        command=['sh', 'run.sh'],
        time_limit_seconds=5,
        memory_limit_mb=128,
    )

    assert result.exit_code == 0
    assert len(result.stdout.encode('utf-8')) <= 32
    assert 'stdout truncated' in result.logs
