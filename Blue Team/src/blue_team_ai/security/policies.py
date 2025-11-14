from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import BaseModel, ValidationError, validator

from ..config import AppSettings
from .hitl import HITLService
from .rbac import RBACService
from ..utils.logging import audit_log, security_log


class ToolPayload(BaseModel):
    input: str
    rationale: str

    @validator("input")
    def sanitize_input(cls, value: str) -> str:
        if len(value) > 5000:
            raise ValueError("Input too long")
        return value


@dataclass
class PolicyRule:
    role: str
    tool: str
    hitl_required: bool = False


class PolicyEnforcer:
    def __init__(self, settings: AppSettings, rbac: Optional[RBACService] = None, hitl: Optional[HITLService] = None) -> None:
        self.settings = settings
        self.rbac = rbac or RBACService()
        self.hitl = hitl or HITLService()
        # Only enumerate HITL-sensitive tools here; authorization is driven by RBAC
        self.rules: List[PolicyRule] = [
            PolicyRule(role="admin", tool="issue_reimbursement", hitl_required=True),
            PolicyRule(role="admin", tool="update_bank_account", hitl_required=True),
        ]

    def validate(self, *, tool_name: str, role: str, payload: Dict) -> None:
        self._validate_payload(tool_name, payload)
        self._enforce_role(tool_name, role)
        self._enforce_hitl(tool_name, role, payload)

    def _validate_payload(self, tool_name: str, payload: Dict) -> None:
        try:
            ToolPayload(**payload)
        except ValidationError as exc:
            security_log("payload_validation_failed", severity="warning", tool=tool_name, errors=exc.errors())
            raise

    def _enforce_role(self, tool_name: str, role: str) -> None:
        if not self.rbac.check_permission(role, tool_name):
            security_log("policy_violation", severity="error", tool=tool_name, role=role)
            raise PermissionError(f"Role {role} not authorized for {tool_name}")

    def _enforce_hitl(self, tool_name: str, role: str, payload: Dict) -> None:
        for rule in self.rules:
            if rule.tool == tool_name and rule.role == role and rule.hitl_required:
                request_id = f"{tool_name}:{payload.get('input', '')[:20]}"
                self.hitl.create_request(request_id=request_id, tool_name=tool_name, requested_by=role, rationale=payload.get("rationale", ""))
                audit_log("hitl_required", tool=tool_name, role=role, request_id=request_id)
                raise PermissionError("Human-in-the-loop approval required")

