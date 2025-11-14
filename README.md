# Cursor Template

- This repo is a template for a Cursor project v0.1
- It includes project specific rule files you can use an LLM to change
- The plan is to try and make a migration script and template everything.
- There has been no development done, only preparation for development
- CAUTION: NOT CHANGING RULES FILES COULD RESULT IN UNCERTAIN OUTCOMES
- Enjoy! 👾

# Achilles Runs

_Achilles Runs_ is the orchestration, CI tracing, and rules enforcement layer for the **Achilles** system, focused on deep observability, test artifact intelligence, and agent lifecycle tracking. This directory serves as the glue between the backend, frontend/dashboard, and CI/CD, capturing signals to enhance **build intelligence** and developer/agent experience.

---

## Mission

- **Trace** all build/test phases for both backend and frontend subsystems
- **Aggregate** CI signals (tests, lint, typing, errors, summaries) in a canonical format
- **Trigger** state/model updates based on build and agent outcomes
- **Enforce** rules aligning to Achilles canonical requirements (see `AGENTS.md`)
- **Empower** future agent or tool integrations for intelligent insights

---

## Key Features

- **CI Artifact Tracing**
  - Runs both backend and frontend CI jobs (`.github/workflows/*-ci.yml`)
  - Collects results in _structured JSON_ (`ci_signals_*`)
  - Uploads CI signals as versioned artifacts after every build

- **State & Milestone Management**
  - `update-state.yml` workflow updates middleware (`state/*.mdc`) upon CI signal arrival
  - Supports both interactive (manual) and automated triggers
  - Passes build phase results to `tools/update_state.py` for canonical state transitions

- **Rule Enforcement**
  - Follows strict, deterministic rules (see `AGENTS.md`)
  - Never mutates raw event logs; all state is recomputable
  - Aligns with Achilles' observability and intelligence mission (no PM/issue management)

- **Extensible for Cursor MCP Server**
  - Designed to integrate with the Cursor MCP server (in development)
  - Will ingest, trace, and correlate agent intelligence signals across developer and agent runs

---

## Directory Layout

| Path                                    | Purpose                                                 |
|------------------------------------------|---------------------------------------------------------|
| `.github/workflows/backend-ci.yml`       | Backend tests, lint, typing, coverage, signal upload    |
| `.github/workflows/frontend-ci.yml`      | Frontend tests, lint, coverage, signal upload           |
| `.github/workflows/update-state.yml`     | Applies CI signals to update state/milestone models     |
| `state/`                                | Backend and frontend state tracking (mdc)               |
| `ci_artifacts/` *(workflow only)*        | Holds CI signal exports for workflow steps              |
| `tools/update_state.py`                  | Applies state transitions based on CI outcomes          |
| `AGENTS.md`                             | _Canonical Agent rules for all processing & control_    |
| `.cursorignore`                         | Local/tooling ignores, not system metadata              |

---

## CI Signal Flow

1. **CI Run**: Each push/PR to backend or frontend triggers respective CI workflows.
2. **Signal Collection**: On completion, results are parsed into strict JSON (e.g. `ci_signals_backend.json`, `ci_signals_frontend.json`).
3. **Artifact Upload**: Signal JSONs are uploaded as versioned artifacts for downstream workflows.
4. **State Update**: `update-state.yml` downloads signal artifacts, parses key results, and calls `update_state.py` to mutate phase state files in `state/`.
5. **Rule Alignment**: All jobs and state transitions comply with locked-down rules in `AGENTS.md`.

---

## Canonical Rules Overview

Achilles Runs **strictly enforces** the operational rules of the Achilles system:

- **No mutation** of raw event logs, ever.
- **All state transitions** must be deterministic and observable.
- **Only ingestion and read-only endpoints**—never add PM/task management.
- **CI signals** must match strictly-typed models, and be traceable across runs.
- **Processing and milestones** must be idempotent and fully recomputable.
- **Agent intelligence** is for observability and improvement, **not for automation**.
- **Cursor MCP Server** integration is strictly for ingestion, mapping, and event transport (never inference/clustering here).

See `AGENTS.md` for canonical requirements and a full decision log for allowed/forbidden changes.

---

## Development

- _In development_: Cursor MCP server and next-gen agent/CI adapters.
- Designed for **maximum observability** and traceable, rule-driven CI intelligence.
- PRs must never expand project management or mutate core event/state logic beyond requirements.

---

## Contact

For questions about Achilles Runs or agent observability pipelines, refer to [AGENTS.md](./AGENTS.md) or contact the Achilles maintainers.

