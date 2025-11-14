from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

try:
    import chromadb  # type: ignore
    from chromadb.config import Settings  # type: ignore
    _CHROMA_AVAILABLE = True
except Exception:  # noqa: BLE001
    chromadb = None  # type: ignore
    Settings = None  # type: ignore
    _CHROMA_AVAILABLE = False

from ..config import DataSettings
from ..utils.logging import get_logger
from .provenance import ProvenanceTracker

logger = get_logger(__name__)


class KnowledgeBaseManager:
    def __init__(self, settings: DataSettings, provenance: ProvenanceTracker) -> None:
        self.settings = settings
        self.provenance = provenance
        if _CHROMA_AVAILABLE:
            try:
                # Prefer persistent client when available (newer API)
                self.client = chromadb.PersistentClient(path=str(settings.data_dir), settings=Settings(is_persistent=True))  # type: ignore[attr-defined]
                self.collections = {
                    "policies": self.client.get_or_create_collection(name=settings.policy_collection),
                    "employees": self.client.get_or_create_collection(name=settings.employees_collection),
                    "finance": self.client.get_or_create_collection(name=settings.finance_collection),
                }
            except Exception:  # noqa: BLE001
                # Fallback for older Chroma API (<=0.4.x)
                self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=str(settings.data_dir)))  # type: ignore[attr-defined]
                self.collections = {
                    "policies": self.client.get_or_create_collection(name=settings.policy_collection),
                    "employees": self.client.get_or_create_collection(name=settings.employees_collection),
                    "finance": self.client.get_or_create_collection(name=settings.finance_collection),
                }
        else:
            # In-memory simple store
            self.client = None
            self.collections = {
                "policies": {},
                "employees": {},
                "finance": {},
            }

    def ingest(self, *, collection: str, items: List[Tuple[str, str, Dict]]) -> None:
        logger.info("knowledge_ingest", collection=collection, count=len(items))
        if _CHROMA_AVAILABLE:
            ids = [item[0] for item in items]
            documents = [item[1] for item in items]
            metadatas = [item[2] for item in items]
            self.collections[collection].add(ids=ids, documents=documents, metadatas=metadatas)
            for metadata in metadatas:
                self.provenance.record(source_id=metadata.get("source_id", "unknown"), action="ingest", details=metadata)
        else:
            for _id, doc, meta in items:
                self.collections[collection][_id] = {"document": doc, "metadata": meta}
                self.provenance.record(source_id=meta.get("source_id", "unknown"), action="ingest", details=meta)

    def query(self, *, collection: str, text: str, k: int = 5) -> List[Dict]:
        logger.info("knowledge_query", collection=collection)
        matches: List[Dict] = []
        if _CHROMA_AVAILABLE:
            results = self.collections[collection].query(query_texts=[text], n_results=k)
            for docs, metas in zip(results["documents"], results["metadatas"]):
                for doc, meta in zip(docs, metas):
                    matches.append({"document": doc, "metadata": meta})
                    self.provenance.record(
                        source_id=meta.get("source_id", "unknown"),
                        action="query",
                        details={"query": text, "collection": collection},
                    )
            return matches
        # Simple substring match fallback
        store: Dict[str, Dict] = self.collections[collection]
        for _id, entry in store.items():
            doc = entry["document"]
            meta = entry["metadata"]
            if text.lower() in doc.lower():
                matches.append({"document": doc, "metadata": meta})
                self.provenance.record(
                    source_id=meta.get("source_id", "unknown"),
                    action="query",
                    details={"query": text, "collection": collection},
                )
            if len(matches) >= k:
                break
        return matches

