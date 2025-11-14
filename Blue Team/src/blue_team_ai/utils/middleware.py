from __future__ import annotations

from typing import Awaitable, Callable, Dict

from .anomaly import AnomalyDetector


class InstrumentationMiddleware:
    def __init__(self, anomaly_detector: AnomalyDetector) -> None:
        self.anomaly_detector = anomaly_detector

    async def __call__(self, *, tool_name: str, role: str, session_id: str, handler: Callable[[], Awaitable[Dict]]) -> Dict:
        self.anomaly_detector.record_event(tool_name=tool_name, role=role, session_id=session_id)
        result = await handler()
        return result

