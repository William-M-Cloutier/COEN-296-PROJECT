from __future__ import annotations

from typing import Dict, List, Optional

from ..config import AppSettings, get_settings
from ..utils import AnomalyDetector, InstrumentationMiddleware
from ..utils.logging import audit_log, configure_logging, get_logger
from .aggregator import AgentResponse, ResponseAggregator
from .planner import PlannedStep, TaskPlanner
from .state import SessionStateStore
from .tool_router import AgentRouter

logger = get_logger(__name__)


class AgentOrchestrator:
    """Coordinates planning, routing, and aggregation for enterprise workflows."""

    def __init__(
        self,
        router: AgentRouter,
        aggregator: ResponseAggregator,
        state_store: SessionStateStore,
        settings: AppSettings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        configure_logging(self.settings.log_level)
        self.router = router
        self.aggregator = aggregator
        self.state_store = state_store
        self.anomaly_detector = AnomalyDetector()
        self.middleware = InstrumentationMiddleware(self.anomaly_detector)
        self.planner = TaskPlanner()

    async def handle_request(self, *, session_id: str, role: str, request: str, data: Optional[Dict] = None) -> Dict:
        audit_log("request_received", session_id=session_id, role=role)
        self.state_store.append_message(session_id, "user", request)
        planned_steps = await self.planner.plan(request, data)
        responses = await self._execute_plan(session_id=session_id, role=role, steps=planned_steps)
        aggregated = self.aggregator.synthesize(responses)
        self.state_store.append_message(session_id, "system", str(aggregated))
        audit_log("response_generated", session_id=session_id)
        return aggregated

    async def _execute_plan(self, *, session_id: str, role: str, steps: List[PlannedStep]) -> List[AgentResponse]:
        responses: List[AgentResponse] = []
        for step in steps:
            payload = {"action": step.action, **step.params, "rationale": step.rationale}
            async def handler() -> Dict:
                return await self.router.dispatch(session_id=session_id, tool_name=step.agent, payload=payload, role=role)

            result = await self.middleware(tool_name=step.agent, role=role, session_id=session_id, handler=handler)
            responses.append(AgentResponse(tool=step.agent, output=result, rationale=step.rationale))
        return responses

