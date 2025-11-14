from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from ..utils.logging import audit_log


@dataclass
class TestCase:
    name: str
    description: str
    execute: Callable[[], Any]


class RedTeamHarness:
    def __init__(self) -> None:
        self.tests: List[TestCase] = []

    def add_test(self, test: TestCase) -> None:
        self.tests.append(test)

    async def run_all(self) -> Dict[str, Any]:
        results = {}
        for test in self.tests:
            try:
                outcome = test.execute()
                if asyncio.iscoroutine(outcome):
                    outcome = await outcome
                results[test.name] = {"status": "pass", "details": outcome}
            except Exception as exc:  # noqa: BLE001
                results[test.name] = {"status": "fail", "error": str(exc)}
        audit_log("red_team_suite_completed", results=list(results.keys()))
        return results

