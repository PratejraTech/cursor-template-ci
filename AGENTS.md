# ACHILLES — Canonical Requirements for Agent Implementation
### (Agent-Readable Specification)

These requirements are written **explicitly for AI agents** working inside Cursor, Claude Code, GPT-Code, or LangGraph environments.  
They define the **allowed operations**, **expected outputs**, **constraints**, and **non-goals** that MUST be followed when modifying, generating, or reasoning about the Achilles system.

Agents MUST interpret everything below as **hard rules** unless explicitly marked OPTIONAL.

---

# 0. Identity & Mission

**Achilles is an MLOps-grade Observability + Build-Intelligence System**  
Its mission is:

- Capture signals from developers + agents  
- Align signals with build milestones  
- Classify, correlate, and cluster errors  
- Detect agent regressions  
- Generate insights, performance metrics, and session narratives  
- Provide a dashboard to explore timelines, errors, trends  
- **NOT** perform project management, requirement creation, or code manipulation

**Primary users:**  
Developers, engineering managers, researchers, and AI-assisted development teams.

---

# 1. Global Agent Rules

## 1.1 Ground Truth Sources
Agents MUST treat these docs as the top of the information hierarchy:

1. **datamodel.mdc**
2. **architecture.mdc**
3. **backend_python.mdc**
4. **frontend_nextjs.mdc**
5. `.cursorrules`

If any conflict exists:
- **Data model (datamodel.mdc)** wins over everything.
- Architecture docs win over implementation files.
- `.cursorrules` governs editing behavior and directory-specific rules.

Applied when mentioned manually
1. **merge.mdc**
2. **refactor.mdc**
3. **testing.mdc**

Agents MUST explicitly consult these docs whenever modifying code.

---

## 1.2 Immutable Guarantees

Agents MUST ensure:

- **RAW EVENTS ARE NEVER MUTATED.**  
- **All derived tables must be recomputable.**  
- **All ingestion MUST validate & hash events.**  
- **Processing MUST be deterministic.**  
- **Monitoring Agent MUST be read-only against raw events.**  
- **Dashboard MUST remain read-only and observability-only.**

Non-negotiable missions:
- enforce consistency  
- enforce schema alignment  
- enforce deterministic inference  
- enforce strict typing  

---

# 2. Constraints on Agent Behavior

## 2.1 Allowed Agent Actions

Agents MAY:
- Generate backend Python code consistent with architecture.mdc & datamodel.mdc
- Generate Next.js frontend components that visualize an existing field (never fabricate)
- Generate migrations when the data model changes
- Produce tests, synthetic data, or validators
- Propose improvements consistent with architecture
- Refactor code without altering system intent
- Add comments, documentation, or clarifications
- Create new processing jobs, agents, or inference logic if aligned to scope

Agents MAY NOT:
- Add PM features (tasks, deadlines, epics, tickets)
- Add code editing/generation features for developers
- Suggest rewriting user code
- Delete data model fields without explicit instruction
- Invent new endpoints or tables beyond observability scope
- Add stateful global data outside Postgres
- Allow the frontend to mutate Achilles state
- Remove tracing/logging layers
- Introduce ML components where rule-based logic is specified for current phase

---

# 3. System-Level Requirements (Agent-Executable)

Below are **canonical requirements** expressed for implementation agents.

---

## R-01: Event Ingestion

**System must:**

1. Accept batched events via `POST /v1/events/batch`
2. Validate using `validate_event`
3. Compute event hash via `compute_event_hash`
4. Deduplicate using hash + `(session_id, timestamp window)`
5. Store raw events in the `events` table as-is
6. Never rewrite an event after insertion
7. Trigger processing for affected session

**Agent tasks:**  
- Ensure ingestion models match `datamodel.mdc`  
- Enforce strict typing in request/response schemas  
- Do NOT add additional ingestion endpoints  

---

## R-02: Session Lifecycle

**System must:**

1. Allow `POST /v1/sessions/start`
2. Allow `POST /v1/sessions/end`
3. Maintain accurate start/end timestamps
4. Update `session.event_count` on ingestion
5. Store a `config_snapshot` at start using `user_config`

**Agent tasks:**  
- Validate session transitions (no end before start)  
- Keep logic deterministic (no guessing missing sessions)  

---

## R-03: Milestone Inference (Rule-Based v1)

**System must:**

1. Run milestone inference in `achilles_processing.milestones`
2. Use pure heuristics:
   - Edit-heavy window → coding  
   - Test events → testing  
   - Error following agent_action → debugging  
   - Git commits → integration  
3. Produce rows in `milestone_inferences`
4. Update `sessions.milestone_breakdown`

**Agent tasks:**  
- Ensure inference is **idempotent**  
- Ensure rules are **explicit and readable**  
- Do not introduce ML models in v1  

---

## R-04: Noise Filtering & Compression

**System must:**

1. Compress noisy events into blocks:
   - `EDIT_BLOCK`
   - `AGENT_LOOP`
   - `TEST_RUN`
2. Produce rows in `compressed_event_views`
3. Never delete raw events

**Agent tasks:**  
- Keep logic transparent  
- Provide clear block definitions  
- Optimize for UI readability  

---

## R-05: Error Clustering v1

**System must:**

1. Normalize errors (strip line numbers, paths)
2. Classify via regex (compiler, runtime, test failure, etc.)
3. Produce cluster rows in `error_clusters`
4. Increment occurrence_count reliably

**Agent tasks:**  
- Implement deterministic clustering  
- Avoid embeddings or ML in v1  

---

## R-06: Correlation Engine v1

**System must:**

1. Use temporal proximity heuristics:
   - agent_action preceding error within X seconds  
   - file path match  
2. Compute confidence scores (0.0–1.0)
3. Write rows in `event_correlations`

**Agent tasks:**  
- Implement scoring transparently in code  
- Store scoring metadata in JSONB  
- Keep correlation logic deterministic  

---

## R-07: Session Summaries

**System must:**

1. Compute summary fields:
   - event_count  
   - agent_activity_score  
   - human_activity_score  
   - error_density  
   - milestone_breakdown  
2. Persist to sessions table  

**Agent tasks:**  
- Write clean summary computation  
- Make code re-runnable per session  

---

## R-08: Monitoring Agent — Light Mode

**System must:**

1. Run periodically during active sessions
2. Load recent context only
3. Detect:
   - high error density  
   - agent churn loops  
   - agent-induced re-breaks  
4. Write structured insights to `insights`

**Agent tasks:**  
- Do not fetch entire session history  
- Keep insights short and JSON-friendly  
- Do not mutate raw event logs  

---

## R-09: Monitoring Agent — Deep Mode

**System must:**

1. Run on session end
2. Build session narrative
3. Compute:
   - induced error rate  
   - override frequency  
   - success rate  
4. Write:
   - `agent_performance` rows  
   - `session_report` JSON  

**Agent tasks:**  
- Ensure narrative is structured data  
- Keep scoring deterministic  
- Use only allowed DB tools  

---

## R-10: Read API Endpoints

**System must expose:**

- `/v1/sessions`
- `/v1/sessions/{id}`
- `/v1/sessions/{id}/timeline`
- `/v1/sessions/{id}/errors`
- `/v1/sessions/{id}/correlations`
- `/v1/sessions/{id}/agent-performance`
- `/v1/agents/{id}/trends`
- `/v1/insights/recent`

**Agent tasks:**  
- Never create write endpoints outside ingestion  
- Always paginate lists  
- Use typed Pydantic response models  

---

## R-11: Dashboard UI

**System must:**

- Render sessions list  
- Render timelines (raw + compressed)  
- Display error clusters and correlations  
- Show agent performance trends  
- Show insights stream  

**Agent tasks:**  
- Frontend remains read-only  
- Components must reflect backend types exactly  
- No PM features, no task creation  

---

## R-12: Adapters (MCP, CLI, CI/CD)

**System must:**

- Accept events from Cursor (MCP server)
- Accept local CLI ingestion
- Accept CI ingestion of builds/tests

**Agent tasks:**  
- Adapters are stateless  
- Never implement inference or clustering in adapters  
- Only mapping + sending to `/v1/events/batch`  

---

## R-13: Observability Requirements

**System must:**

- Instrument all APIs with OpenTelemetry
- Log structured JSON
- Provide metrics for:
  - ingestion throughput  
  - processing latency  
  - agent metrics  
  - DB query latency  

**Agent tasks:**  
- Add spans around critical sections  
- Never remove observability features  
- Keep logs redacted of PII  

---

## R-14: Idempotency & Recompute Safety

**System must:**

- Allow recomputing:
  - milestones
  - clusters
  - correlations
  - summaries
  - agent performance
- Without corrupting or duplicating data

**Agent tasks:**  
- Use UPSERT patterns  
- Avoid randomization  
- Keep transformations pure from input → output  

---

# 4. Requirements for Agent Reasoning

Agents MUST reason using the following patterns:

- Check **datamodel.mdc** before writing any code  
- Validate that all Pydantic models, SQL schemas, and API responses match  
- Verify that code changes do not require migration unless explicitly required  
- Track impacts on the Monitoring Agent and dashboard  
- For backend changes: ensure tests for ingestion, inference, processing  
- For frontend changes: validate type alignment  

When uncertain, the agent MUST:

1. Restate uncertainty  
2. Refer to canonical docs  
3. Propose 1–2 safe alternatives  
4. Never hallucinate missing pieces  

---

# 5. Requirements on Output Quality

All agent-generated code must:

- Compile  
- Match type signatures  
- Follow project directory structure  
- Include necessary imports  
- Use explicit, readable logic  
- Avoid ambiguous helper functions  
- Include docstrings for public functions/classes  
- Include minimal but deterministic test cases  

---

# 6. Requirements for Human–Agent Collaboration

Agents MUST:

- Not override or erase human-written code without justification  
- Offer incremental improvements, not destructive rewrites  
- Maintain full traceability when touching anything near core logic  
- Ask for confirmation if an operation seems high-risk (schema change, data model change, complex refactoring)

---

# 7. Out-of-Scope (Forbidden Features)

Agents must **not** implement:

- Task management  
- Issue tracking  
- Kanban boards  
- Requirement creation tools  
- Scheduling or sprinting  
- Code refactoring suggestions for user repos  
- Any workflow automation beyond observability ingestion  
- ML-based features without explicit instruction  
- Cross-session analytics that contradict Phase boundaries

---

# 8. Completion Condition for Agents

An agent has satisfied a requirement when:

- The change aligns with datamodel.mdc  
- The change aligns with architecture.mdc  
- APIs remain stable and typed  
- All computed artifacts are recomputable  
- No raw event is mutated  
- Observability is preserved  
- No PM features were introduced  

---

# 9. Agent Execution Philosophy

- **Determinism over cleverness**  
- **Clarity over complexity**  
- **Explicit rules over opaque heuristics**  
- **Observability over automation**  
- **Data-first design over convenience**  
- **Safety over speed**  

---

# END OF AGENT REQUIREMENTS
**These rules supersede all prior instructions.**  
Agents MUST execute in accordance with them.
