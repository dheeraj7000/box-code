from __future__ import annotations

import typer

from .executor import LocalExecutor
from .models import ExecutionRequest
from .policy import CommandPolicy

app = typer.Typer(help="Run bounded commands for the Box-Code sandbox agent.")


@app.command()
def run(
    command: str = typer.Argument(..., help="Shell command to execute."),
    workspace: str = typer.Option("/workspace", help="Allowed workspace directory."),
    timeout: float = typer.Option(10.0, min=0.1, max=120.0, help="Timeout in seconds."),
) -> None:
    """Validate and execute one command."""
    request = ExecutionRequest(
        command=command,
        working_directory=workspace,
        timeout_seconds=timeout,
    )
    decision = CommandPolicy(workspace).validate(request)
    if not decision.allowed:
        typer.echo(f"Blocked: {decision.reason}", err=True)
        raise typer.Exit(code=2)
    if decision.requires_confirmation:
        typer.echo(f"Confirmation required: {decision.reason}", err=True)
        raise typer.Exit(code=3)

    result = LocalExecutor().execute(request)
    if result.stdout:
        typer.echo(result.stdout, nl=False)
    if result.stderr:
        typer.echo(result.stderr, err=True, nl=False)
    if result.timed_out:
        raise typer.Exit(code=124)
    raise typer.Exit(code=result.exit_code or 0)


if __name__ == "__main__":
    app()
