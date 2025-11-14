from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol

from ..security.signing import SignatureService
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgentContext:
    session_id: str
    role: str


class SecureAgent(Protocol):
    name: str

    async def execute(self, *, session_id: str, payload: Dict) -> Dict:
        ...


class SignedAgentMixin:
    def __init__(self, signature_service: SignatureService) -> None:
        self.signature_service = signature_service

    def sign(self, payload: Dict) -> Dict:
        logger.info("signing_payload", payload_keys=list(payload.keys()))
        return self.signature_service.wrap_message(payload)

    def verify(self, message: Dict) -> Dict:
        logger.info("verifying_payload")
        return self.signature_service.unwrap_message(message)

