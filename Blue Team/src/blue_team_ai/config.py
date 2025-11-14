from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, BaseSettings, SecretStr, AnyHttpUrl


class RBACRole(BaseModel):
    name: str
    permissions: List[str]


class ObservabilitySettings(BaseModel):
    otlp_endpoint: Optional[AnyHttpUrl] = None
    service_name: str = "blue-team-copilot"
    enable_metrics: bool = True
    enable_traces: bool = True


class SecuritySettings(BaseModel):
    jwt_secret: SecretStr = SecretStr("insecure-change-me")
    hmac_shared_secret: SecretStr = SecretStr("insecure-hmac-change-me")
    token_expiry_minutes: int = 30
    session_ttl_minutes: int = 60
    credential_ttl_minutes: int = 5
    sensitive_tool_allowlist: List[str] = ["issue_reimbursement", "update_bank_account"]
    sensitive_tool_requires_hitl: List[str] = ["issue_reimbursement", "update_bank_account"]


class LLMSettings(BaseModel):
    completion_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-large"
    temperature: float = 0.2
    max_tokens: int = 2048


class DataSettings(BaseModel):
    data_dir: Path = Path("./storage")
    policy_collection: str = "policies"
    employees_collection: str = "employees"
    finance_collection: str = "finance"
    provenance_log: Path = Path("./storage/provenance.log")


class AppSettings(BaseSettings):
    env: str = "development"
    log_level: str = "INFO"
    openai_api_key: SecretStr = SecretStr("not-set")
    llm: LLMSettings = LLMSettings()
    data: DataSettings = DataSettings()
    security: SecuritySettings = SecuritySettings()
    observability: ObservabilitySettings = ObservabilitySettings()
    default_admin_email: str = "admin@example.com"
    default_admin_password: SecretStr = SecretStr("please-change")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = "APP_"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()

