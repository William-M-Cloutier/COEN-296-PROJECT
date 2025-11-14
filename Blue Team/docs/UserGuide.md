# Blue Team Enterprise Copilot User Guide

This guide explains how to interact with the Blue Team Enterprise Copilot CLI, data workflows, and security controls.

## Roles

- `admin`: Approves sensitive actions (reimbursements, bank updates).
- `employee`: Submits expenses, retrieves policies.
- `auditor`: Reviews audit logs and observability outputs.

## Setup

1. Copy `configs/env.example` → `.env` and update credentials.
2. Install dependencies:
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - Ensure CLI import path (choose one):
     - Quick: `export PYTHONPATH="$(pwd)/src"` (set this in your shell before CLI commands)
     - Recommended: `python -m pip install --upgrade pip && python -m pip install -e .` (requires modern pip; enables `blue_team_ai` imports)
3. Bootstrap knowledge bases: `python scripts/bootstrap_system.py`.

## Authentication

Authenticate with seeded admin credentials:

```
# If using PYTHONPATH:
export PYTHONPATH="$(pwd)/src"
python -m blue_team_ai.interfaces.cli login admin@example.com please-change
# Or run via file path (no PYTHONPATH needed):
python src/blue_team_ai/interfaces/cli.py login admin@example.com please-change
```

Use the token in API contexts or run CLI commands with `--role`.

## API Usage

- Start the API:
  - `uvicorn blue_team_ai.interfaces.api:app --reload --port 8000`
- Health:
  - `GET http://localhost:8000/health`
- Submit task:
  - `POST http://localhost:8000/tasks`
  - Body:
    ```json
    {
      "task": "process expense reimbursement",
      "data": {
        "employee_id": "emp-001",
        "amount": 200.0,
        "category": "travel",
        "description": "Taxi from airport"
      }
    }
    ```
- View events:
  - `GET http://localhost:8000/logs`
- Run safe red-team test (hallucination detection demo):
  - `POST http://localhost:8000/tests/rt-01`

## System Architecture

### Component overview

- **Interfaces**
  - **API**: FastAPI app (`src/blue_team_ai/interfaces/api.py`) exposes endpoints for health, task submission, knowledge base operations, safe red-team tests, and sensitive expense actions.
  - **CLI**: Typer-based CLI (`src/blue_team_ai/interfaces/cli.py`) for local requests and authentication workflows.
- **Core**
  - **AgentOrchestrator** (`core/orchestrator.py`): Coordinates planning, routing, execution, and aggregation. Maintains short-term session memory and wraps execution with instrumentation.
  - **TaskPlanner** (`core/planner.py`): Heuristic, security-aware planner that decomposes a user request into a sequence of agent steps; avoids external LLM dependency by default.
  - **AgentRouter** (`core/tool_router.py`): Dispatches steps to agent tools, enforcing policy (RBAC + HITL) before execution and signing messages for secure agent-to-agent calls.
  - **ResponseAggregator** (`core/aggregator.py`): Synthesizes multiple agent outputs into a structured result.
  - **SessionStateStore** (`core/state.py`): TTL-backed in-memory conversation and notes per `session_id`.
- **Agents**
  - **ExpenseAgent, EmailAgent, DriveAgent** (`agents/*.py`): Implement business actions (submit/review/issue reimbursement; send email; upload/search/retrieve docs). Agents use `SignedAgentMixin` for HMAC-based message signing/verification.
- **Security**
  - **AuthService** (`security/auth.py`): Local JWT auth with seeded admin; used by CLI.
  - **RBACService** (`security/rbac.py`): Role→permission mapping. Examples: `employee` can `submit`, `admin` can `issue_reimbursement` and `update_bank_account`.
  - **PolicyEnforcer** (`security/policies.py`): Validates payload shape, checks RBAC, and enforces Human-In-The-Loop (HITL) on sensitive tools.
  - **HITLService** (`security/hitl.py`): Tracks approval requests; blocks execution until approved.
  - **SignatureService** (`security/signing.py`): HMAC-SHA256 signing of inter-agent messages.
- **Data**
  - **KnowledgeBaseManager** (`data/knowledge_base.py`): Pluggable vector store (Chroma if available; in-memory fallback) for policies, employees, finance.
  - **ProvenanceTracker** (`data/provenance.py`): Appends immutable provenance entries to `storage/provenance.log`.
- **Observability**
  - **Structured logging** (`utils/logging.py`): `audit.jsonl` and `security.jsonl` under `./logs`, plus console output.
  - **Instrumentation + Anomaly detection** (`utils/middleware.py`, `utils/anomaly.py`): Records tool usage per role and flags spikes.

### Request flow (API)

1. Client calls `POST /tasks` with a task and optional data.
2. API builds an `AgentOrchestrator` (config, agents, router, enforcer, aggregator, state store) and logs the event.
3. Orchestrator:
   - Appends user message to `SessionStateStore`.
   - `TaskPlanner.plan` → list of `PlannedStep` items (agent, action, params, rationale).
   - For each step:
     - `AgentRouter.dispatch` enforces policy:
       - Validates payload shape.
       - Checks RBAC for the requested action.
       - If action is sensitive and role requires approval, `HITLService` records a request and a `PermissionError` is raised (execution blocked).
     - On pass, payload is signed (if agent supports it) and `agent.execute` runs.
   - `ResponseAggregator.synthesize` combines results.
   - System response is appended to `SessionStateStore` and returned.

### Security model

- **RBAC**: Role→permission list governs allowed actions. Denials are logged to `security.jsonl`.
- **HITL**: For `issue_reimbursement` and `update_bank_account`, admins require explicit approval before execution; requests are auditable via `HITLService`.
- **Message integrity**: Agent messages are signed and verified with HMAC using `SignatureService`.
- **Auth (CLI)**: JWTs issued by `AuthService`; token claims include role and expiry based on settings.
- **Input validation**: `PolicyEnforcer` validates `input` length and presence of `rationale` for traceability.

### Data and storage

- **Vector store**: Chroma persistent client under `./storage` when installed; otherwise an in-memory fallback is used.
- **Collections**: `policies`, `employees`, `finance`.
- **Provenance**: All KB ingest/query actions are recorded to `storage/provenance.log`.
- **Logs**: `./logs/audit.jsonl` and `./logs/security.jsonl` capture structured evidence. API emits `events.jsonl` for UI/demo timelines.

### Observability and auditability

- Audit trail for requests, tool invocations, HITL events, and provenance.
- Security log for policy violations, anomalies, and verification failures.
- Lightweight anomaly detection flags abnormal tool usage by role over a sliding window.

### Extensibility

- Add a new agent by implementing `execute(session_id, payload)` and (optionally) `sign/verify` via `SignedAgentMixin`, then register it in the orchestrator’s tool map.
- Extend planner heuristics to emit new `PlannedStep`s for your agent.
- Add RBAC permissions and, if sensitive, a `PolicyRule` and HITL requirement.

### Deployment

- API runs with Uvicorn (`uvicorn blue_team_ai.interfaces.api:app --reload --port 8000`).
- Configuration via `.env` and `AppSettings` (`src/blue_team_ai/config.py`), prefixed with `APP_` (e.g., `APP_LOG_LEVEL`, `APP_SECURITY__JWT_SECRET`).
- `LOG_DIR` env controls log file location; defaults to `./logs`.
- Red-team evidence for `RT-01` is persisted under `redteam/results/RT-01/`.

## Submitting an Expense

```
# Using module path (requires PYTHONPATH or editable install):
export PYTHONPATH="$(pwd)/src"
python -m blue_team_ai.interfaces.cli request session1 employee "Submit expense report for employee emp-001 amount 250 category travel"
# Or run the script directly:
python src/blue_team_ai/interfaces/cli.py request session1 employee "Submit expense report for employee emp-001 amount 250 category travel"
```

## Review and Reimbursement (Admin HITL)

```
export PYTHONPATH="$(pwd)/src"
python -m blue_team_ai.interfaces.cli request session1 admin "Review expense report report-123"
python -m blue_team_ai.interfaces.cli request session1 admin "Issue reimbursement for report-123"
# Or:
python src/blue_team_ai/interfaces/cli.py request session1 admin "Review expense report report-123"
python src/blue_team_ai/interfaces/cli.py request session1 admin "Issue reimbursement for report-123"
```

## Retrieve Policies

```
export PYTHONPATH="$(pwd)/src"
python -m blue_team_ai.interfaces.cli request session2 employee "Search document policy"
# Or:
python src/blue_team_ai/interfaces/cli.py request session2 employee "Search document policy"
```

## Notes

- Sensitive actions enforce allowlist + HITL.
- All tool invocations are logged to the audit trail.
- Refer to `docs/ThreatModelOutline.md` and `docs/RedTeamTestSuiteOutline.md` for security evidence procedures.
