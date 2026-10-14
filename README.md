# Box-Code

Box-Code is a sandboxed, Claude Code–style software engineering agent foundation. It validates and executes bounded terminal commands inside a controlled workspace, with a design that can later support LLM-driven coding workflows.

## Phase 1 status

This branch contains the first execution foundation:

- Python 3.12+ package and CLI
- Structured Pydantic request/result models
- Conservative command policy
- Timeout and output-size limits
- Restricted environment variables
- Unit tests for execution and policy behavior

> The current `LocalExecutor` is a development executor. Run it inside a disposable, non-root container before using it with untrusted input. The policy layer is defense-in-depth, not a security boundary.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Usage

The default workspace is `/workspace`; create it first when running locally:

```bash
mkdir -p /workspace
box-code 'hello from Box-Code'
```

The CLI command is exposed as:

```bash
box-code run 'printf "hello\\n"' --workspace /workspace
```

Commands such as package installation and Git operations are reported as requiring confirmation. Blocked programs are rejected. The next implementation phase will add a Docker-backed executor and explicit approval handling.

## Roadmap

1. Docker/Podman sandbox executor
2. Workspace lifecycle manager
3. File inspection and editing tools
4. LLM adapter and multi-step agent loop
5. Audit logging and approval workflow
6. Optional FastAPI service
