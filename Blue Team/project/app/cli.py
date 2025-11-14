from __future__ import annotations

import sys
from pathlib import Path

# Ensure local 'src' is on sys.path for direct execution without editable install
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from blue_team_ai.interfaces.cli import app  # Typer app

if __name__ == "__main__":
    app()


