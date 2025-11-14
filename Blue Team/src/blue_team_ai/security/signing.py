from __future__ import annotations

import hmac
import secrets
from hashlib import sha256
from typing import Dict

from ..config import AppSettings
from ..utils.logging import security_log


class SignatureService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def sign(self, message: str) -> str:
        secret = self.settings.security.hmac_shared_secret.get_secret_value().encode("utf-8")
        signature = hmac.new(secret, msg=message.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature

    def verify(self, message: str, signature: str) -> bool:
        expected = self.sign(message)
        is_valid = secrets.compare_digest(expected, signature)
        if not is_valid:
            security_log("signature_verification_failed", severity="warning")
        return is_valid

    def wrap_message(self, payload: Dict) -> Dict:
        serialized = str(sorted(payload.items()))
        signature = self.sign(serialized)
        return {"payload": payload, "signature": signature}

    def unwrap_message(self, message: Dict) -> Dict:
        payload = message.get("payload", {})
        signature = message.get("signature", "")
        serialized = str(sorted(payload.items()))
        if not self.verify(serialized, signature):
            raise ValueError("Invalid message signature")
        return payload

