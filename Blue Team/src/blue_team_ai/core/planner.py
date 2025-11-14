from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import uuid4

from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PlannedStep:
    agent: str
    action: str
    params: Dict
    rationale: str


class TaskPlanner:
    """Security-aware heuristic planner that decomposes tasks into agent steps without external LLMs."""

    def __init__(self) -> None:
        pass

    async def plan(self, request: str, data: Optional[Dict] = None) -> List[PlannedStep]:
        logger.info("planning_task", request=request)
        # Heuristic planner for offline environments
        steps = self._fallback_plan(request, data or {})
        logger.info("plan_completed", step_count=len(steps))
        return steps

    def _fallback_plan(self, request: str, data: Dict) -> List[PlannedStep]:
        lower = request.lower()
        # Email tasks
        if "email" in lower or "send email" in lower:
            params = {
                "sender": data.get("sender", "noreply@enterprise.com"),
                "recipient": data.get("recipient", "employee@enterprise.com"),
                "subject": data.get("subject", "No subject"),
                "body": data.get("body", request),
            }
            return [PlannedStep(agent="email_agent", action="send", params=params, rationale="Send email")]
        # Document/Drive tasks
        if "document" in lower or "drive" in lower or "upload" in lower:
            if "upload" in lower:
                doc_id = data.get("doc_id", f"doc-{uuid4().hex[:6]}")
                params = {
                    "doc_id": doc_id,
                    "title": data.get("title", "Untitled"),
                    "content": data.get("content", ""),
                    "tags": data.get("tags", ["uploaded"]),
                }
                return [PlannedStep(agent="drive_agent", action="upload", params=params, rationale="Upload document")]
            if "search" in lower:
                params = {"keyword": data.get("keyword", "policy")}
                return [PlannedStep(agent="drive_agent", action="search", params=params, rationale="Search documents")]
            if "retrieve" in lower or "get" in lower:
                params = {"doc_id": data.get("doc_id", "policy_v1")}
                return [PlannedStep(agent="drive_agent", action="retrieve", params=params, rationale="Retrieve document")]
            # Default document action is search
            params = {"keyword": data.get("keyword", "policy")}
            return [PlannedStep(agent="drive_agent", action="search", params=params, rationale="Search documents")]
        # Expense workflow
        if "expense" in lower or "reimburse" in lower or "reimbursement" in lower:
            report_id = data.get("report_id", f"rpt-{uuid4().hex[:6]}")
            employee_id = data.get("employee_id", "emp-001")
            amount = float(data.get("amount", 100.0))
            category = data.get("category", "travel")
            description = data.get("description", "Auto-submitted by planner")
            return [
                PlannedStep(
                    agent="expense_agent",
                    action="submit",
                    params={
                        "report_id": report_id,
                        "employee_id": employee_id,
                        "amount": amount,
                        "currency": data.get("currency", "USD"),
                        "category": category,
                        "description": description,
                    },
                    rationale="Submit expense report",
                ),
                PlannedStep(
                    agent="expense_agent",
                    action="review",
                    params={"report_id": report_id},
                    rationale="Policy-based automated review",
                ),
                PlannedStep(
                    agent="expense_agent",
                    action="issue_reimbursement",
                    params={"report_id": report_id},
                    rationale="Issue reimbursement if approved",
                ),
            ]
        # Default: no-op search for policy
        return [
            PlannedStep(
                agent="drive_agent",
                action="search",
                params={"keyword": "policy"},
                rationale="Default route to policy search",
            )
        ]

