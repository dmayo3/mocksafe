# AGENTS.md

## Purpose
Guide AI coding agents working in this repo. Keep changes minimal, explicit, and test-backed.

## Source of truth (read before editing)
- Project overview/API: `README.rst`
- User-facing behavior and examples: `docs/usage.rst`, `docs/typesafety.rst`, `docs/plugin.rst`
- Contribution workflow: `CONTRIBUTING.md`
- Release workflow: `RELEASE_PROCESS.md`
- Tooling/dependencies: `pyproject.toml`, `tox.ini`, `.pre-commit-config.yaml`
- Real behavior contracts: `tests/`

Prefer linking to these files over duplicating policy text.

## Engineering principles
- KISS + YAGNI: implement only what the task asks for.
- Preserve public API and semantics unless explicitly requested.
- Favor small, isolated edits over broad refactors.
- Don't introduce new dependencies unless very clearly justified.
- Keep type-safety guarantees intact (core value of MockSafe).
  - Never suppress/ignore type issues unless explicit permission or instruction is given.
  - Same goes for weakening type checking configuration.
s
## Change workflow
1. Understand current behavior from docs + tests before coding.
2. Edit the smallest set of files needed.
3. Add/update tests for behavior changes.
4. Run relevant checks locally (targeted first, then broader if needed).
5. Ensure docs/examples stay accurate when API/behavior changes.

## Validation targets
- Tests: `uvx tox` (or focused envs/paths while iterating)
- Type checks: `uvx tox -e mypy`, `uvx tox -e pyright`
- Lint/format: `uvx tox -e lint`, `uvx tox -e format`
- Pre-commit (recommended): `uv run pre-commit run --all-files`

## Coding expectations
- Python >= 3.10; follow existing style (Black, 100-char lines).
- Keep signatures and typing precise; avoid unnecessary `Any`.
- Match established naming/patterns in `mocksafe/core` and `mocksafe/apis`.
- For pytest plugin work, preserve optional-import behavior in `mocksafe/plugin.py`.

## PR/commit quality bar
- Clear intent, no incidental churn.
- Tests prove the change.
- Docs updated only when needed.
- No speculative cleanup unrelated to the task.
