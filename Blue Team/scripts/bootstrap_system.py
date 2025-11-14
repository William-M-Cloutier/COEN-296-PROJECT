from __future__ import annotations

from pathlib import Path

from blue_team_ai.config import get_settings
from blue_team_ai.data import KnowledgeBaseManager, ProvenanceTracker

POLICY_DOCS = [
    (
        "policy_v1",
        "Travel and expense reimbursements require manager approval for amounts above $1000.",
        {"source_id": "policy_v1", "category": "policy", "version": "1.0"},
    )
]

EMPLOYEE_DOCS = [
    (
        "emp-001",
        "Employee Alice Employee, role employee, reports to manager@enterprise.com.",
        {"source_id": "emp-001", "category": "employee", "role": "employee"},
    )
]

FINANCE_DOCS = [
    (
        "finance-emp-001",
        "Employee Alice Employee bank account ending 3000 with balance 1200.",
        {"source_id": "finance-emp-001", "category": "finance", "sensitivity": "high"},
    )
]


def main() -> None:
    settings = get_settings()
    settings.data.data_dir.mkdir(parents=True, exist_ok=True)
    provenance = ProvenanceTracker(settings.data)
    kb = KnowledgeBaseManager(settings.data, provenance)
    kb.ingest(collection="policies", items=POLICY_DOCS)
    kb.ingest(collection="employees", items=EMPLOYEE_DOCS)
    kb.ingest(collection="finance", items=FINANCE_DOCS)
    print("Bootstrap completed.")


if __name__ == "__main__":
    main()

