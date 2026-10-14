from __future__ import annotations

from pathlib import Path

from box_code.executor import LocalExecutor
from box_code.models import ExecutionRequest
from box_code.policy import CommandPolicy


def test_executor_captures_stdout(tmp_path: Path) -> None:
    request = ExecutionRequest(command="printf 'hello'", working_directory=str(tmp_path))
    result = LocalExecutor().execute(request)

    assert result.stdout == "hello"
    assert result.stderr == ""
    assert result.exit_code == 0
    assert result.timed_out is False


def test_executor_times_out(tmp_path: Path) -> None:
    request = ExecutionRequest(
        command="sleep 1",
        working_directory=str(tmp_path),
        timeout_seconds=0.05,
    )
    result = LocalExecutor().execute(request)

    assert result.timed_out is True
    assert result.exit_code is None


def test_policy_blocks_dangerous_program(tmp_path: Path) -> None:
    request = ExecutionRequest(command="sudo whoami", working_directory=str(tmp_path))
    decision = CommandPolicy(str(tmp_path)).validate(request)

    assert decision.allowed is False


def test_policy_requires_confirmation_for_git(tmp_path: Path) -> None:
    request = ExecutionRequest(command="git status", working_directory=str(tmp_path))
    decision = CommandPolicy(str(tmp_path)).validate(request)

    assert decision.allowed is True
    assert decision.requires_confirmation is True


def test_policy_rejects_outside_workspace(tmp_path: Path) -> None:
    request = ExecutionRequest(command="pwd", working_directory="/tmp")
    decision = CommandPolicy(str(tmp_path)).validate(request)

    assert decision.allowed is False
