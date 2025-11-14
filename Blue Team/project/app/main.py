from __future__ import annotations

import sys
from pathlib import Path

# Ensure local 'src' is on sys.path for direct uvicorn execution without editable install
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Expose the FastAPI app for uvicorn entrypoint in starter layout
from blue_team_ai.interfaces.api import app  # noqa: F401


