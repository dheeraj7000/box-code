from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExecutionRequest(BaseModel):
    """Validated request for one command executed inside the workspace."""

    model_config = ConfigDict(extra="forbid")

    command: str = Field(min_length=1, max_length=4096)
    working_directory: str = "/workspace"
    timeout_seconds: float = Field(default=10.0, gt=0, le=120)

    @field_validator("working_directory")
    @classmethod
    def validate_working_directory(cls, value: str) -> str:
        if not Path(value).is_absolute():
            raise ValueError("working_directory must be an absolute path")
        return value


class ExecutionResult(BaseModel):
    """Serializable result returned by a sandbox executor."""

    command: str
    stdout: str
    stderr: str
    exit_code: int | None
    duration_ms: int = Field(ge=0)
    timed_out: bool = False
    output_truncated: bool = False


class PolicyDecision(BaseModel):
    allowed: bool
    reason: str
    requires_confirmation: bool = False
