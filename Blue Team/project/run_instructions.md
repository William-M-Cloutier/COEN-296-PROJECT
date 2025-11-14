# COEN 296 PROJECT — Run Instructions (Starter Service)

These steps start the example Blue Team service locally using pinned dependencies.

## Prerequisites
- Python 3.10+
- pip

## Setup
1. Create and activate a virtual environment:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Initialize local storage and seed mock data:
   - `python scripts/bootstrap_system.py`

Optional: Create a `.env` (based on `configs/env.example`) to override defaults.

## Start the Example Service
Run the FastAPI app with Uvicorn:
- `uvicorn blue_team_ai.interfaces.api:app --reload --port 8000`
  or using the starter-style path:
- `uvicorn project.app.main:app --reload --port 8000`

Health check:
- `GET http://localhost:8000/health` → `{"status": "ok"}`

## Available Endpoints
- `POST /tasks` — submit a task for planning and safe simulated execution
- `GET  /logs` — fetch structured event logs (sanitized)
- `POST /tests/rt-01` — run a safe red-team (hallucination) simulation

Notes:
- All actions are local-only and use safe mock data and enforcement (RBAC, HITL, signatures, anomaly detection).
- Evidence and logs are stored under `redteam/results/` and `./logs/`.

## Demo Script (Safe)
Use the provided walkthrough script to exercise the API and collect evidence.
1. Ensure the server is running on `http://localhost:8000`
2. In another terminal (same venv):
   - `python run_demo.py --base-url http://localhost:8000`

The script will:
- Call `/tasks` with a sample request
- Call `/tests/rt-01` to run the safe red-team simulation
- Fetch `/logs`
- Save sanitized evidence under `redteam/results/collected_evidence_<ts>.json`

## Troubleshooting
- If `/tasks` returns a planning error, ensure the server is running and that you’re using the pinned versions in `requirements.txt`.
- Use a fresh virtual environment if dependency conflicts appear.


