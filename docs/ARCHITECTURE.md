Phase 1 – Data & Core Library Only

Goal: One canonical truth: the data model + validation. No services yet.

Components

Postgres

Holds the core MVP tables:

events

sessions

error_clusters

event_correlations

agent_performance

insights

Managed by Alembic migrations.

achilles_core (Python package)

Pydantic models that mirror datamodel.mdc.

SQLAlchemy models tied directly to those tables.

Validation module:

validate_event

validate_session

compute_event_hash

Config module:

Central Settings (DB URL, env, OTEL endpoint, flags).

Logging / tracing bootstrap (minimal, shared later by services).

Architecture Shape

There is no networked architecture yet.

This phase is basically:

achilles_core ↔ Postgres via SQLAlchemy

You can interact via:

Alembic CLI

Python scripts / notebooks that use achilles_core

Key Architectural Decisions

Data model is treated as API: all later phases depend on it.

achilles_core is the only package allowed to define models and validation.

Nothing else is allowed to talk to the DB without going through achilles_core.

Phase 2 – Ingestion API (Single Service + DB)

Goal: Add a single network-facing service to ingest and read raw events/sessions.

Components

achilles_api (FastAPI service)

Runs as a single container/process initially.

Responsibilities:

Accept sessions and batched events.

Validate and hash events.

Deduplicate.

Write to Postgres.

Provide minimal read endpoints.

CLI / Simple Adapter

adapters/cli_tool – a tiny Python CLI that:

Calls /v1/sessions/start

Calls /v1/events/batch

Calls /v1/sessions/end

Reads /v1/sessions/{id} and /v1/sessions/{id}/events

Postgres

Same as Phase 1, but now populated via the API.

achilles_core

Imported by achilles_api for:

Pydantic models (request/response)

SQLAlchemy models (persistence)

Validation + hashing

Settings/logging/tracing

Data Flow

CLI/adapter → HTTP → achilles_api.

achilles_api:

parses payload → Pydantic model

runs validate_event

computes event_hash

dedupes

writes to Postgres via SQLAlchemy.

Read side:

/v1/sessions/{id} and /v1/sessions/{id}/events query Postgres and return JSON.

Deployment View

Minimal Docker Compose:

achilles_api container

postgres container

Optional: OTEL collector later, but you can at least add tracing hooks now.

Architectural Boundaries

Only one service talks to DB: achilles_api.

Validation logic remains in achilles_core, not inline in routes.

No processing/worker yet – no background analytics.

Phase 3 – Processing Worker (Two Services + DB)

Goal: Add a separate processing service that turns raw events into error clusters, correlations, and simple summaries.

Components

achilles_api (FastAPI)

Unchanged responsibilities from Phase 2.

May gain a tiny internal call or “enqueue” hook to send work to processing (even if that’s just setting a “needs_processing” flag).

achilles_processing (Worker service)

Runs as a separate container/process.

Responsibilities:

Periodically query Postgres for sessions needing processing.

For each session:

Load events.

Build MVP error clusters (regex-based).

Build MVP correlations (time window + file match).

Compute simple session summary:

event_count

agent_activity_score

error_density

Write to:

error_clusters

event_correlations

sessions summary fields.

Execution model:

Start simple:

A loop: “scan for work → process session → sleep”.

Later you can plug this into a job queue (Redis/RQ, etc.), but not required for MVP.

Postgres

Now stores both raw and derived data.

achilles_core

Shared by both achilles_api and achilles_processing.

Provides:

Consistent models

Validation

DB connection/access helpers

Config

Data Flow

Ingestion:

Same as Phase 2: CLI → achilles_api → Postgres (events, sessions).

Processing:

achilles_processing periodically:

SELECT sessions needing processing.

SELECT events for each session.

Compute clusters/correlations/summary.

UPSERT into derived tables and sessions summary fields.

Reading:

Still only the minimal read endpoints, but now if you query the DB you’ll see derived data.

Deployment View

Docker Compose:

achilles_api

achilles_processing

postgres

They share:

network (bridge)

DB connection

achilles_core package (same version across services)

Architectural Boundaries

achilles_processing does not accept HTTP traffic (MVP).

No direct calls from achilles_processing back to achilles_api – all communication is via DB.

All business logic for analytics lives in achilles_processing (milestone-like logic deferred for later; here it’s just clustering/correlation/summary).

Both services respect achilles_core as the single schema source.

Phase 4 – Monitoring Agent + Extended Read APIs (Three Services + DB)

Goal: Add a lightweight Monitoring Agent (LangGraph) and extend APIs so a dashboard/IDE can consume insights and performance metrics.

Components

achilles_api (FastAPI)

Still handles ingestion.

Now also exposes richer read endpoints for:

/v1/sessions/{id}/errors

/v1/sessions/{id}/correlations

/v1/sessions/{id}/agent-performance

/v1/insights/recent

Optionally:

/v1/sessions/{id}/summary (aggregated view).

achilles_processing (Worker)

Same as Phase 3: generates clusters, correlations, summaries.

May also mark sessions as “ready” for deep analysis (e.g., after end event).

achilles_agent (Monitoring Agent service)

New service running LangGraph.

Responsibilities:

Light agent mode (can be triggered periodically or via API/callback):

Load last N events and summary for an active session.

Check for patterns:

high error density

agent churn (repeat break/fix)

Emit minimal structured insights rows into DB.

Deep agent mode (triggered on session end or manually):

Load all events, clusters, correlations, summary.

Compute:

total agent actions

induced error count (from correlations)

MVP success_rate

Write:

agent_performance rows

optionally a small session_report JSON (can live in an extra column or separate table later).

Uses achilles_core models and DB helpers.

Exposes LangGraph graphs internally; you might add a tiny HTTP control interface for manual triggering, but MVP can run on timers / job triggers.

Postgres

Single shared DB:

Raw tables (events, sessions)

Derived tables (error_clusters, event_correlations, agent_performance, insights)

achilles_core

Shared library across all three services.

Data Flow

End-to-end MVP scenario:

Ingestion:

CLI/adapter → achilles_api → events + sessions.

Processing:

achilles_processing → reads events → writes error_clusters, event_correlations, updated sessions.

Monitoring Agent:

achilles_agent:

Light mode: looks at latest events + summary → writes insights for active sessions.

Deep mode (on session end): reads full session data → writes agent_performance + possibly insights.

Consumption:

A future dashboard or IDE plugin calls achilles_api read endpoints:

sessions details

errors

correlations

agent performance

recent insights

Deployment View

Docker Compose / K8s:

achilles_api (HTTP ingress)

achilles_processing (worker)

achilles_agent (LangGraph service)

postgres

Optionally:

OTEL collector

Log aggregation

Architectural Boundaries

achilles_api:

Only service exposed externally (for now).

Only writes raw/ingested data (plus maybe simple metadata).

achilles_processing:

Sole owner of MVP analytics (clusters, correlations, summaries).

Never mutates raw events.

achilles_agent:

Sole owner of higher-level evaluation (insights + agent_performance).

Read-only on raw/derived tables; writes to insights and agent_performance.

No service is allowed to bypass the data model or validation in achilles_core.