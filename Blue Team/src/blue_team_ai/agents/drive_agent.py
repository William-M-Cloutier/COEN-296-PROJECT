from __future__ import annotations

from typing import Dict, List

from .base import SignedAgentMixin
from .mock_data import DOCUMENTS, DocumentRecord
from ..utils.logging import audit_log, get_logger

logger = get_logger(__name__)


class DriveAgent(SignedAgentMixin):
    name = "drive_agent"

    def __init__(self, signature_service) -> None:
        super().__init__(signature_service)

    async def execute(self, *, session_id: str, payload: Dict) -> Dict:
        message = self.verify(payload)
        action = message.get("action")
        audit_log("drive_agent_execute", session_id=session_id, action=action)
        if action == "upload":
            return self._upload_document(message)
        if action == "retrieve":
            return self._retrieve_document(message)
        if action == "search":
            return self._search_documents(message)
        raise ValueError(f"Unsupported drive action {action}")

    def _upload_document(self, message: Dict) -> Dict:
        doc_id = message["doc_id"]
        DOCUMENTS[doc_id] = DocumentRecord(title=message["title"], content=message["content"], tags=message.get("tags", []))
        audit_log("document_uploaded", doc_id=doc_id, title=message["title"])
        return {"status": "uploaded", "doc_id": doc_id}

    def _retrieve_document(self, message: Dict) -> Dict:
        doc_id = message["doc_id"]
        document = DOCUMENTS.get(doc_id)
        if not document:
            return {"status": "not_found"}
        return {"status": "ok", "document": document.__dict__}

    def _search_documents(self, message: Dict) -> Dict:
        keyword = message.get("keyword", "").lower()
        results = [
            {"doc_id": doc_id, **document.__dict__}
            for doc_id, document in DOCUMENTS.items()
            if keyword in document.title.lower() or keyword in document.content.lower() or keyword in " ".join(document.tags).lower()
        ]
        return {"status": "ok", "results": results}

