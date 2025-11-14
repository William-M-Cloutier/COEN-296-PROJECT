# Project Layout (Starter Style)

This directory mirrors the starter repo layout for readability.

- `app/` — entrypoints and thin wrappers around the main package
  - `main.py` exposes the FastAPI `app`
  - `agent.py` helper to build the orchestrator
  - `retriever.py` helper to access the knowledge base

You can run the service as:

```
uvicorn project.app.main:app --reload --port 8000
```

For full documentation and details, see the root `README.md` and `run_instructions.md`.


