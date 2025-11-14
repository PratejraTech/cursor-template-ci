PHASE 1 — DATA FOUNDATIONS (MVP)

Objective: Establish the minimal data backbone to make the system ingestible, testable, and recomputable.

Implement only the essential tables:

events

sessions

error_clusters

event_correlations

agent_performance

insights

(Milestones and compressed views can be added later—MVP omits them.)

Create matching Pydantic models and SQLAlchemy models for each table.
Only include fields required for basic ingestion, error grouping, correlations, and agent scoring.

Implement minimal validation:

validate_event for event_type, timestamp, source_type

compute_event_hash for dedupe
No advanced rules, no normalization beyond basic safety checks.

Create an initial Alembic migration that builds the MVP schema.

Add Settings/config loader in achilles_core.

Acceptance:
The database schema applies cleanly, models match tables, validation works, and events can be represented faithfully.

PHASE 2 — INGESTION + MINIMAL API (MVP)

Objective: Allow real event streams to flow into Achilles with minimal friction.

Add FastAPI service with:

POST /v1/sessions/start

POST /v1/sessions/end

POST /v1/events/batch

GET /v1/sessions/{id}

GET /v1/sessions/{id}/events

Ingestion rules:

Validate using MVP validation module

Compute hash

Deduplicate based on (event_hash, session_id, timestamp window)

Persist raw events directly

No derived processing, no worker, no clustering, no correlation yet in this phase.

Create a tiny CLI client that:

starts a session

sends 20–50 events

ends the session

Acceptance:
API can store and return events in order. A full session can be ingested and retrieved. CLI confirms round-trip.

PHASE 3 — PROCESSING ENGINE MVP (CLUSTERS + CORRELATIONS + SIMPLE SUMMARY)

Objective: Produce the minimum intelligence layer required to show value.

Build a lightweight worker (single-threaded polling or manual trigger) that:

Loads session events

Groups errors by normalized message (strip file paths + line numbers)

Creates basic error_clusters rows

Creates simple correlations:

agent_action preceding an error by ≤ 10 seconds

same file match → confidence 0.7

otherwise confidence 0.4

Add a tiny session summary:

event_count

basic agent_activity_score (count agent events)

basic error_density (errors per 100 events)

Write updated summaries back to the sessions table.

No milestones, no editing blocks, no noise compression in MVP.

Acceptance:
Given a session containing agent actions and errors, the worker produces minimally correct:

error clusters

event correlations

summary fields

Data remains deterministic and re-runnable.

PHASE 4 — MONITORING AGENT MVP + ESSENTIAL READ APIS

Objective: Deliver the smallest possible “actionable intelligence” layer through a simple monitoring agent and basic dashboard-facing endpoints.

Implement a minimal LangGraph agent with only two nodes:

load_basic_context: load the last N events + summary + clusters

detect_basic_insights: produce simple insights such as:

“High error density”

“Agent likely caused recent error”

“Repeated break-fix cycle detected”

Insights are structured small JSON objects written to the insights table.

Implement the minimal agent_performance computation:

total_actions

induced_error_count (from correlations)

success_rate = (actions - induced errors) / actions

Add minimal read APIs:

GET /v1/sessions/{id}/errors

GET /v1/sessions/{id}/correlations

GET /v1/sessions/{id}/agent-performance

GET /v1/insights/recent

No deep narrative, no multi-step graph, no trend analysis. Strictly MVP.

Acceptance:
With a synthetic session containing agent refactor → failing test → human fix, the system:

ingests all events

clusters errors

correlates agent action to error

updates performance metrics

monitoring agent produces at least one insight

read endpoints return stable typed responses.