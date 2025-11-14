from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
import asyncio

from blue_team_ai.interfaces.api import app
from blue_team_ai.interfaces.cli import build_orchestrator
from blue_team_ai.security.signing import SignatureService
from blue_team_ai.agents.email_agent import EmailAgent
from blue_team_ai.config import get_settings
from blue_team_ai.data import KnowledgeBaseManager, ProvenanceTracker


def test_hallucination_detection_endpoint():
    client = TestClient(app)
    resp = client.post("/tests/rt-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["summary"]["flagged_count"] >= 1


def test_expense_issue_requires_hitl():
    orchestrator = build_orchestrator()
    with pytest.raises(PermissionError):
        # Admin can perform 'review' but 'issue_reimbursement' requires HITL and should be blocked
        asyncio.run(
            orchestrator.handle_request(
                session_id="s1",
                role="admin",
                request="process expense reimbursement",
                data={"employee_id": "emp-001", "amount": 200.0, "category": "travel"},
            )
        )


def test_signature_rejection_on_unsigned_message():
    settings = get_settings()
    sig = SignatureService(settings)
    agent = EmailAgent(sig)
    with pytest.raises(ValueError):
        # Missing signature wrapper
        asyncio.run(
            agent.execute(
                session_id="s2",
                payload={"action": "send", "sender": "a@b.com", "recipient": "c@d.com", "subject": "x", "body": "y"},
            )
        )


def test_provenance_canary_ingestion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    settings = get_settings()
    # Use temp dir for storage to avoid polluting real logs
    monkeypatch.setattr(settings.data, "data_dir", tmp_path / "storage")
    monkeypatch.setattr(settings.data, "provenance_log", tmp_path / "storage" / "prov.log")
    kb = KnowledgeBaseManager(settings.data, ProvenanceTracker(settings.data))
    kb.ingest(collection="policies", items=[("canary-123", "THIS IS A CANARY DOC", {"source_id": "canary-123", "tag": "canary"})])
    _ = kb.query(collection="policies", text="CANARY", k=1)
    # Verify provenance contains canary source
    log_path = settings.data.provenance_log
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert any("canary-123" in line for line in lines)


