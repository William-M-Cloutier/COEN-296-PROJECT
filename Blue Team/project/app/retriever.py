from __future__ import annotations

from blue_team_ai.config import get_settings
from blue_team_ai.data import KnowledgeBaseManager, ProvenanceTracker


def get_kb() -> KnowledgeBaseManager:
    """Return a KnowledgeBaseManager using current settings with provenance tracking."""
    settings = get_settings()
    provenance = ProvenanceTracker(settings.data)
    return KnowledgeBaseManager(settings.data, provenance)


