from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgentResponse:
    tool: str
    output: Dict
    rationale: str


class ResponseAggregator:
    """Combines agent responses into a synthesized result for the user."""

    def synthesize(self, responses: List[AgentResponse]) -> Dict:
        logger.info("aggregating_responses", count=len(responses))
        summary: Dict[str, List[Dict]] = {}
        for resp in responses:
            summary.setdefault(resp.tool, []).append({"output": resp.output, "rationale": resp.rationale})
        # Simple synthesis for now; can be replaced with LLM summarization if needed.
        return {
            "summary": {tool: self._summarize_outputs(entries) for tool, entries in summary.items()},
            "raw": [resp.output for resp in responses],
        }

    def _summarize_outputs(self, entries: List[Dict]) -> Dict:
        if not entries:
            return {"status": "no-output"}
        combined_status = {entry["output"].get("status", "ok") for entry in entries}
        return {
            "status": " & ".join(sorted(combined_status)),
            "details": entries,
        }

