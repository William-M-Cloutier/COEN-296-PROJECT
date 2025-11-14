from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Deque, Dict, List

from .logging import security_log


@dataclass
class ActionEvent:
    timestamp: datetime
    tool_name: str
    role: str
    session_id: str


class AnomalyDetector:
    def __init__(self, window_seconds: int = 300, threshold: int = 10) -> None:
        self.window = timedelta(seconds=window_seconds)
        self.threshold = threshold
        self.events: Deque[ActionEvent] = deque()

    def record_event(self, tool_name: str, role: str, session_id: str) -> None:
        event = ActionEvent(timestamp=datetime.utcnow(), tool_name=tool_name, role=role, session_id=session_id)
        self.events.append(event)
        self._prune()
        self._check_anomaly(tool_name, role)

    def _prune(self) -> None:
        cutoff = datetime.utcnow() - self.window
        while self.events and self.events[0].timestamp < cutoff:
            self.events.popleft()

    def _check_anomaly(self, tool_name: str, role: str) -> None:
        count = sum(1 for event in self.events if event.tool_name == tool_name and event.role == role)
        if count > self.threshold:
            security_log("anomaly_detected", severity="warning", tool=tool_name, role=role, count=count)

