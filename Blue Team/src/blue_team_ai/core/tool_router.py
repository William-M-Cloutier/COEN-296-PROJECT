from __future__ import annotations

from typing import Dict, Protocol

from ..security.policies import PolicyEnforcer
from ..utils.logging import audit_log, get_logger, security_log

logger = get_logger(__name__)


class AgentTool(Protocol):
    name: str

    async def execute(self, *, session_id: str, payload: Dict) -> Dict:
        ...


class AgentRouter:
    """Routes planned steps to the appropriate agent tool with policy enforcement."""

    def __init__(self, tools: Dict[str, AgentTool], enforcer: PolicyEnforcer) -> None:
        self.tools = tools
        self.enforcer = enforcer

    async def dispatch(self, *, session_id: str, tool_name: str, payload: Dict, role: str) -> Dict:
        logger.info("dispatch_request", tool=tool_name, role=role)
        if tool_name not in self.tools:
            security_log("tool_not_found", severity="error", tool=tool_name, session_id=session_id)
            raise ValueError(f"Unknown tool {tool_name}")

        tool = self.tools[tool_name]
        # Enforce policy on the specific action being requested
        action = payload.get("action", "")
        rationale = payload.get("rationale", "")
        self.enforcer.validate(tool_name=action, role=role, payload={"input": str({k: v for k, v in payload.items() if k != 'rationale'}), "rationale": rationale})
        audit_log("tool_invocation", tool=tool_name, role=role, session_id=session_id)
        # Prepare signed message for inter-agent communication
        to_agent = {k: v for k, v in payload.items() if k != "rationale"}
        if hasattr(tool, "sign"):
            signed = tool.sign(to_agent)  # type: ignore[attr-defined]
            result = await tool.execute(session_id=session_id, payload=signed)
        else:
            result = await tool.execute(session_id=session_id, payload=to_agent)
        audit_log("tool_response", tool=tool_name, session_id=session_id, status="success")
        return result

