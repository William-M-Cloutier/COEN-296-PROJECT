# Blue Team Enterprise Copilot

An agentic AI application that implements layered defenses, observability, and evidence-backed red team testing for an enterprise copilot handling email, document, and expense workflows. The project is designed for the COEN 296 capstone as the Blue Team deliverable.

## Key Capabilities

- **Core Orchestration**: Planner, routing, and response aggregation built on LLM tools with session memory.
- **Specialized Agents**: Dedicated email, drive, and expense agents with scoped credentials and policy enforcement.
- **RAG Data Layer**: Vector-backed knowledge bases for policies, employee profiles, and financial accounts with provenance tracking.
- **Security Controls**: Role-based access, allow/deny lists, human-in-the-loop gates, signed agent communication, and anomaly detection.
- **Observability**: Structured logging, audit trails, metrics, and defensive alerting mapped to MAESTRO layers.
- **Red Team Test Harness**: Automated ASI taxonomy-aligned adversarial tests to validate controls and produce evidence for threat modeling.

## Getting Started

1. Create and populate a `.env` file based on `configs/env.example`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Initialize local stores and seed data: `python scripts/bootstrap_system.py`.
4. Launch the API server: `uvicorn blue_team_ai.interfaces.api:app --reload --port 8000`.
5. (Optional) Launch the CLI: `python -m blue_team_ai.interfaces.cli`.

Refer to `docs/UserGuide.md` for detailed interaction instructions.

See `project/run_instructions.md` for step-by-step instructions to start the example service.

## Project Structure

```
src/blue_team_ai/
  core/           # Planner, orchestrator, state store, tool manager
  agents/         # Email, Drive, Expense specialized agents
  data/           # Vector stores, ingestion pipelines, HR/finance DB
  security/       # RBAC, policy guards, signatures, anomaly detection
  interfaces/     # CLI/API surface, adapters, presentation logic
  utils/          # Shared utilities (logging, config, tracing)
docs/             # Architecture diagrams, guides, threat model drafts
configs/          # Environment templates, policy configs, RBAC rules
tests/            # Unit/integration and red-team automation suites
scripts/          # Data ingestion, bootstrap, maintenance scripts
```

## Blue Team Scope

- Extends MAESTRO defensive requirements with additional controls (network sandboxing, distributed rate limiting, policy linting).
- Captures and evidences red team exercises, aligning mitigations with EU AI Act governance controls.
- Produces comprehensive documentation: architecture, threat model, governance mapping, system audit, and reporting templates.

## Contributing

1. Run `ruff` and `pytest` before submitting changes.
2. Update documentation for any user-facing change.
3. Record defensive evidence in `docs/` for red team interactions.

## License

MIT License. See `LICENSE` for details.


## Demo walkthrough (safe)

Use the included `project/run_demo.py` to exercise the API and collect sanitized evidence.

1. Start the server:
   - `uvicorn blue_team_ai.interfaces.api:app --reload --port 8000`
2. In another terminal:
   - `python project/run_demo.py --base-url http://localhost:8000`

The script will:
- POST `/tasks` with a sample expense-processing prompt
- POST `/tests/rt-01` to run a safe hallucination-detection simulation
- GET `/logs` to fetch structured event logs
- Save evidence under `redteam/results/collected_evidence_<ts>.json`

