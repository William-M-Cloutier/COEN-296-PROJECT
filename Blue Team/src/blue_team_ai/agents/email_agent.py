from __future__ import annotations

from typing import Dict, List

from .base import SignedAgentMixin
from .mock_data import EMAILS, EmailRecord
from ..utils.logging import audit_log, get_logger

logger = get_logger(__name__)


class EmailAgent(SignedAgentMixin):
    name = "email_agent"

    def __init__(self, signature_service) -> None:
        super().__init__(signature_service)

    async def execute(self, *, session_id: str, payload: Dict) -> Dict:
        message = self.verify(payload)
        action = message.get("action")
        audit_log("email_agent_execute", session_id=session_id, action=action)
        if action == "send":
            return self._send_email(message)
        if action == "list":
            return self._list_emails(message)
        if action == "filter":
            return self._filter_emails(message)
        raise ValueError(f"Unsupported email action {action}")

    def _send_email(self, message: Dict) -> Dict:
        EMAILS.append(
            EmailRecord(
                sender=message["sender"],
                recipient=message["recipient"],
                subject=message["subject"],
                body=message["body"],
                folder="sent",
            )
        )
        audit_log("email_sent", recipient=message["recipient"], subject=message["subject"])
        return {"status": "sent"}

    def _list_emails(self, message: Dict) -> Dict:
        folder = message.get("folder", "inbox")
        emails = [email.__dict__ for email in EMAILS if email.recipient == message["recipient"] and email.folder == folder]
        return {"status": "ok", "emails": emails}

    def _filter_emails(self, message: Dict) -> Dict:
        keyword = message.get("keyword")
        recipient = message["recipient"]
        filtered = [
            email.__dict__
            for email in EMAILS
            if email.recipient == recipient and (keyword.lower() in email.subject.lower() or keyword.lower() in email.body.lower())
        ]
        return {"status": "ok", "emails": filtered}

