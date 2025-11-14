from __future__ import annotations

from typing import Dict

from .base import SignedAgentMixin
from .mock_data import DOCUMENTS, EMPLOYEE_PROFILES, ExpenseReport
from ..utils.logging import audit_log, get_logger, security_log

logger = get_logger(__name__)


class ExpenseAgent(SignedAgentMixin):
    name = "expense_agent"

    def __init__(self, signature_service) -> None:
        super().__init__(signature_service)
        self.expenses: Dict[str, ExpenseReport] = {}

    async def execute(self, *, session_id: str, payload: Dict) -> Dict:
        message = self.verify(payload)
        action = message.get("action")
        audit_log("expense_agent_execute", session_id=session_id, action=action)
        if action == "submit":
            return self._submit_report(message)
        if action == "review":
            return self._review_report(message)
        if action == "issue_reimbursement":
            return self._issue_reimbursement(message)
        if action == "update_bank_account":
            return self._update_bank_account(message)
        raise ValueError(f"Unsupported expense action {action}")

    def _submit_report(self, message: Dict) -> Dict:
        report_id = message["report_id"]
        self.expenses[report_id] = ExpenseReport(
            employee_id=message["employee_id"],
            amount=message["amount"],
            currency=message.get("currency", "USD"),
            category=message["category"],
            description=message.get("description", ""),
        )
        audit_log("expense_submitted", report_id=report_id, employee_id=message["employee_id"])
        return {"status": "submitted", "report_id": report_id}

    def _review_report(self, message: Dict) -> Dict:
        report_id = message["report_id"]
        policy_doc = DOCUMENTS.get("policy_v1")
        if not policy_doc:
            security_log("policy_missing", severity="warning", report_id=report_id)
            return {"status": "error", "reason": "Policy not available"}

        report = self.expenses.get(report_id)
        if not report:
            return {"status": "not_found"}

        if report.amount > 1000:
            report.status = "manager_review"
        else:
            report.status = "approved"
        audit_log("expense_reviewed", report_id=report_id, status=report.status)
        return {"status": "ok", "report": report.__dict__}

    def _issue_reimbursement(self, message: Dict) -> Dict:
        report_id = message["report_id"]
        report = self.expenses.get(report_id)
        if not report:
            return {"status": "not_found"}

        employee = EMPLOYEE_PROFILES.get(report.employee_id)
        if not employee:
            return {"status": "error", "reason": "Employee not found"}

        if report.status != "approved":
            security_log("reimbursement_denied", severity="warning", report_id=report_id, status=report.status)
            return {"status": "error", "reason": "Report not approved"}

        employee["bank_account"]["balance"] += report.amount
        report.status = "paid"
        audit_log("reimbursement_issued", report_id=report_id, employee_id=report.employee_id)
        return {"status": "paid", "balance": employee["bank_account"]["balance"]}

    def _update_bank_account(self, message: Dict) -> Dict:
        employee_id = message.get("employee_id")
        if not employee_id:
            return {"status": "error", "reason": "employee_id is required"}
        employee = EMPLOYEE_PROFILES.get(employee_id)
        if not employee:
            return {"status": "error", "reason": "Employee not found"}
        new_iban = message.get("new_iban")
        balance_delta = message.get("balance_delta")
        balance_set = message.get("balance_set")
        if new_iban:
            employee["bank_account"]["iban"] = new_iban
            audit_log("bank_account_updated", employee_id=employee_id)
        if balance_set is not None:
            try:
                employee["bank_account"]["balance"] = float(balance_set)
            except Exception:  # noqa: BLE001
                return {"status": "error", "reason": "Invalid balance_set"}
            audit_log("bank_balance_set", employee_id=employee_id, balance=employee["bank_account"]["balance"])
        if balance_delta is not None:
            try:
                employee["bank_account"]["balance"] += float(balance_delta)
            except Exception:  # noqa: BLE001
                return {"status": "error", "reason": "Invalid balance_delta"}
            audit_log("bank_balance_changed", employee_id=employee_id, delta=balance_delta)
        return {"status": "ok", "employee_id": employee_id, "bank_account": employee["bank_account"]}

