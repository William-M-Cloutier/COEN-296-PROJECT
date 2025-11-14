from __future__ import annotations

from typing import Dict, List

from .logging import audit_log


class AlertManager:
    def __init__(self) -> None:
        self.alerts: List[Dict] = []

    def raise_alert(self, event: str, severity: str, details: Dict) -> None:
        entry = {"event": event, "severity": severity, "details": details}
        self.alerts.append(entry)
        audit_log("alert_raised", event=event, severity=severity, details=details)

    def list_alerts(self) -> List[Dict]:
        return list(self.alerts)

