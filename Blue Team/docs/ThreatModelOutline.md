# Threat Model Outline (MAESTRO Aligned)

## Foundation Models
- Defenses: Ensemble guardrails, prompt sanitation, response confidence scoring.
- Tests: Ambiguous input prompts to trigger hallucination, check detection.
- Evidence: Logs from `audit` channel showing blocked/flagged responses.

## Data Operations
- Defenses: Provenance tracking, canary documents, schema validation.
- Tests: Canary ingestion, policy tampering attempts.
- Evidence: `provenance.log` entries, anomaly alerts.

## Agent Frameworks
- Defenses: Planner allowlist, HITL on sensitive tools, signed agent messages.
- Tests: Malformed route requests, unauthorized tool invocations.
- Evidence: Policy enforcer denials, signature verification logs.

## Deployment & Infrastructure
- Defenses: Schema validation, sandbox simulation for file ops, scoped credentials.
- Tests: Invalid schema submissions, simulated sandbox escapes.
- Evidence: Error handling logs, sandbox audit trail.

## Evaluation & Observability
- Defenses: Structured logging, metric emission, anomaly detection rules.
- Tests: Simulated covert action, rate limit spikes.
- Evidence: Alert triggers, appended audit entries.

## Security & Compliance
- Defenses: JWT auth, RBAC, secret isolation.
- Tests: Prompt injection for secrets, unauthorized role access attempts.
- Evidence: Security logs, RBAC denial entries.

## Agent Ecosystem
- Defenses: HMAC signatures, mutual verification of agent messages.
- Tests: Forged message injection, signature tampering.
- Evidence: Signature failure logs, rejection telemetry.

