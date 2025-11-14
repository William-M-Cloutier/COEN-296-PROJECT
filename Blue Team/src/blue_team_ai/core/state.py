from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List

from cachetools import TTLCache


@dataclass
class SessionMemory:
    conversation: List[Dict[str, Any]] = field(default_factory=list)
    notes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class SessionStateStore:
    """Stores short-term memory and persisted notes for active sessions."""

    def __init__(self, session_ttl_minutes: int = 60) -> None:
        self._cache: TTLCache[str, SessionMemory] = TTLCache(maxsize=128, ttl=session_ttl_minutes * 60)

    def get(self, session_id: str) -> SessionMemory:
        if session_id not in self._cache:
            self._cache[session_id] = SessionMemory()
        return self._cache[session_id]

    def append_message(self, session_id: str, role: str, content: str) -> None:
        memory = self.get(session_id)
        memory.conversation.append({"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()})

    def add_note(self, session_id: str, key: str, value: Any, expires_in: timedelta | None = None) -> None:
        memory = self.get(session_id)
        memory.notes[key] = {"value": value, "expires_at": (datetime.utcnow() + expires_in).isoformat() if expires_in else None}

    def get_notes(self, session_id: str) -> Dict[str, Any]:
        memory = self.get(session_id)
        valid_notes = {}
        now = datetime.utcnow()
        for key, payload in memory.notes.items():
            expires_at = payload.get("expires_at")
            if expires_at and datetime.fromisoformat(expires_at) < now:
                continue
            valid_notes[key] = payload["value"]
        memory.notes = {k: v for k, v in memory.notes.items() if k in valid_notes}
        return valid_notes

    def reset(self, session_id: str) -> None:
        if session_id in self._cache:
            del self._cache[session_id]

