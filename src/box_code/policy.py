from __future__ import annotations

import shlex
from pathlib import Path

from .models import ExecutionRequest, PolicyDecision


class CommandPolicy:
    """Conservative policy for the first local sandbox prototype."""

    _blocked_programs = {
        "sudo", "su", "mount", "umount", "docker", "podman", "kubectl",
        "ssh", "scp", "nc", "netcat", "reboot", "shutdown", "mkfs",
    }
    _confirmation_programs = {"pip", "pip3", "npm", "pnpm", "yarn", "git"}

    def __init__(self, workspace: str = "/workspace") -> None:
        self.workspace = Path(workspace).resolve()

    def validate(self, request: ExecutionRequest) -> PolicyDecision:
        try:
            parts = shlex.split(request.command)
        except ValueError as exc:
            return PolicyDecision(allowed=False, reason=f"invalid shell syntax: {exc}")

        if not parts:
            return PolicyDecision(allowed=False, reason="command is empty")

        program = Path(parts[0]).name.lower()
        if program in self._blocked_programs:
            return PolicyDecision(allowed=False, reason=f"program '{program}' is blocked")

        try:
            Path(request.working_directory).resolve().relative_to(self.workspace)
        except ValueError:
            return PolicyDecision(allowed=False, reason="working directory is outside workspace")

        if any(token in {"/proc", "/sys", "/dev", "/etc/shadow"} for token in parts):
            return PolicyDecision(allowed=False, reason="sensitive system path is blocked")

        if program in self._confirmation_programs:
            return PolicyDecision(
                allowed=True,
                reason=f"program '{program}' may modify dependencies or repository state",
                requires_confirmation=True,
            )

        return PolicyDecision(allowed=True, reason="command accepted")
