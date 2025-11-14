from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from passlib.context import CryptContext

from ..config import AppSettings
from ..utils.logging import audit_log, security_log

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self._users: Dict[str, Dict[str, str]] = {}
        self._roles: Dict[str, str] = {}
        self._seed_default_admin()

    def _seed_default_admin(self) -> None:
        email = self.settings.default_admin_email
        password = self.settings.default_admin_password.get_secret_value()
        if email not in self._users:
            self._users[email] = {"password": pwd_context.hash(password), "role": "admin"}
            self._roles[email] = "admin"
            audit_log("admin_seeded", email=email)

    def register_user(self, email: str, password: str, role: str) -> None:
        if email in self._users:
            raise ValueError("User already exists")
        self._users[email] = {"password": pwd_context.hash(password), "role": role}
        self._roles[email] = role
        audit_log("user_registered", email=email, role=role)

    def authenticate(self, email: str, password: str) -> str:
        if email not in self._users or not pwd_context.verify(password, self._users[email]["password"]):
            security_log("authentication_failed", severity="warning", email=email)
            raise ValueError("Invalid credentials")
        token = self._create_token(email, self._users[email]["role"])
        audit_log("user_authenticated", email=email)
        return token

    def _create_token(self, email: str, role: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": email,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self.settings.security.token_expiry_minutes)).timestamp()),
        }
        token = jwt.encode(payload, self.settings.security.jwt_secret.get_secret_value(), algorithm="HS256")
        return token

    def verify_token(self, token: str) -> Dict[str, str]:
        try:
            decoded = jwt.decode(token, self.settings.security.jwt_secret.get_secret_value(), algorithms=["HS256"])
            return {"email": decoded["sub"], "role": decoded["role"]}
        except jwt.PyJWTError as exc:
            security_log("token_verification_failed", severity="warning", reason=str(exc))
            raise ValueError("Invalid token") from exc

    def get_role(self, email: str) -> Optional[str]:
        return self._roles.get(email)

