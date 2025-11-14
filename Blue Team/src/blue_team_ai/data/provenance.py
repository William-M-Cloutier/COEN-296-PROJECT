from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from ..config import DataSettings
from ..utils.logging import audit_log


class ProvenanceTracker:
    def __init__(self, settings: DataSettings) -> None:
        self.settings = settings
        self.settings.provenance_log.parent.mkdir(parents=True, exist_ok=True)

    def record(self, *, source_id: str, action: str, details: Dict) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "source_id": source_id,
            "action": action,
            "details": details,
        }
        with self.settings.provenance_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
        audit_log("provenance_recorded", source_id=source_id, action=action)

