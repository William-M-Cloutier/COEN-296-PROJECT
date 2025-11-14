from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..utils.logging import security_log


@dataclass
class RoleDefinition:
    name: str
    permissions: List[str]


class RBACService:
    def __init__(self) -> None:
        self.roles: Dict[str, RoleDefinition] = {
            "admin": RoleDefinition(
                name="admin",
                permissions=[
                    "review",
                    "issue_reimbursement",
                    "update_bank_account",
                    "send",
                    "upload",
                    "retrieve",
                    "search",
                    "list",
                    "filter",
                ],
            ),
            "employee": RoleDefinition(
                name="employee",
                permissions=[
                    "submit",
                    "send",
                    "upload",
                    "retrieve",
                    "search",
                    "list",
                    "filter",
                ],
            ),
            "auditor": RoleDefinition(name="auditor", permissions=["fetch_audit_log"]),
        }

    def check_permission(self, role: str, permission: str) -> bool:
        role_def = self.roles.get(role)
        if not role_def:
            security_log("unknown_role", severity="warning", role=role)
            return False
        has_permission = permission in role_def.permissions
        if not has_permission:
            security_log("permission_denied", severity="warning", role=role, permission=permission)
        return has_permission

