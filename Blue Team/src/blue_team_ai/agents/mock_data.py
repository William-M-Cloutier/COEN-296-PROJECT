from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class EmailRecord:
    sender: str
    recipient: str
    subject: str
    body: str
    folder: str = "inbox"


@dataclass
class DocumentRecord:
    title: str
    content: str
    tags: List[str]


@dataclass
class ExpenseReport:
    employee_id: str
    amount: float
    currency: str
    category: str
    description: str
    status: str = "pending"


EMAILS: List[EmailRecord] = [
    EmailRecord(
        sender="finance@enterprise.com",
        recipient="employee@enterprise.com",
        subject="Policy Update",
        body="Please review the updated reimbursement policy.",
    ),
]

DOCUMENTS: Dict[str, DocumentRecord] = {
    "policy_v1": DocumentRecord(
        title="Expense Policy v1",
        content="Expenses must be approved by managers and follow category limits.",
        tags=["policy", "finance"],
    ),
}

EMPLOYEE_PROFILES: Dict[str, Dict] = {
    "emp-001": {
        "name": "Alice Employee",
        "email": "alice@enterprise.com",
        "role": "employee",
        "manager": "manager@enterprise.com",
        "bank_account": {"iban": "DE89370400440532013000", "balance": 1200.0},
    },
}

