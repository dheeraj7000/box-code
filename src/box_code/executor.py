from __future__ import annotations

import subprocess
import time
from pathlib import Path

from .models import ExecutionRequest, ExecutionResult


class LocalExecutor:
    """Phase 1 executor; intended to run inside a restricted container."""

    def __init__(self, output_limit: int = 100_000) -> None:
        if output_limit <= 0:
            raise ValueError("output_limit must be positive")
        self.output_limit = output_limit

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        started = time.monotonic()
        timed_out = False
        exit_code: int | None = None
        stdout = ""
        stderr = ""

        try:
            completed = subprocess.run(
                ["/bin/sh", "-c", request.command],
                cwd=Path(request.working_directory),
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                check=False,
                env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/tmp"},
            )
            stdout = completed.stdout
            stderr = completed.stderr
            exit_code = completed.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = self._decode(exc.stdout)
            stderr = self._decode(exc.stderr)

        stdout, stdout_truncated = self._limit(stdout)
        stderr, stderr_truncated = self._limit(stderr)
        duration_ms = int((time.monotonic() - started) * 1000)

        return ExecutionResult(
            command=request.command,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_ms=duration_ms,
            timed_out=timed_out,
            output_truncated=stdout_truncated or stderr_truncated,
        )

    def _limit(self, value: str) -> tuple[str, bool]:
        if len(value) <= self.output_limit:
            return value, False
        return value[: self.output_limit] + "\n[output truncated]\n", True

    @staticmethod
    def _decode(value: bytes | str | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value
