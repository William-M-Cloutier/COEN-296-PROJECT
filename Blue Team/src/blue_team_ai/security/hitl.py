from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from ..utils.logging import audit_log, security_log


@dataclass
class ApprovalRequest:
    request_id: str
    tool_name: str
    requested_by: str
    rationale: str
    created_at: datetime
    approved: bool | None = None
    approver: Optional[str] = None


class HITLService:
    def __init__(self) -> None:
        self.requests: Dict[str, ApprovalRequest] = {}

    def create_request(self, request_id: str, tool_name: str, requested_by: str, rationale: str) -> ApprovalRequest:
        approval = ApprovalRequest(
            request_id=request_id,
            tool_name=tool_name,
            requested_by=requested_by,
            rationale=rationale,
            created_at=datetime.utcnow(),
        )
        self.requests[request_id] = approval
        audit_log("hitl_request_created", request_id=request_id, tool_name=tool_name)
        return approval

    def approve(self, request_id: str, approver: str) -> None:
        approval = self.requests.get(request_id)
        if not approval:
            security_log("hitl_request_missing", severity="warning", request_id=request_id)
            raise ValueError("Approval request not found")
        approval.approved = True
        approval.approver = approver
        audit_log("hitl_request_approved", request_id=request_id, approver=approver)

    def deny(self, request_id: str, approver: str) -> None:
        approval = self.requests.get(request_id)
        if not approval:
            security_log("hitl_request_missing", severity="warning", request_id=request_id)
            raise ValueError("Approval request not found")
        approval.approved = False
        approval.approver = approver
        audit_log("hitl_request_denied", request_id=request_id, approver=approver)

    def status(self, request_id: str) -> ApprovalRequest | None:
        return self.requests.get(request_id)

