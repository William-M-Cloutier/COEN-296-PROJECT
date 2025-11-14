from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich.console import Console

from ..agents import DriveAgent, EmailAgent, ExpenseAgent
from ..config import get_settings
from ..core import AgentOrchestrator, AgentRouter, ResponseAggregator, SessionStateStore
from ..security import AuthService, PolicyEnforcer, SignatureService

console = Console()
app = typer.Typer(help="Blue Team Enterprise Copilot CLI")


def build_orchestrator() -> AgentOrchestrator:
    settings = get_settings()
    signature_service = SignatureService(settings)
    tools = {
        "email_agent": EmailAgent(signature_service),
        "drive_agent": DriveAgent(signature_service),
        "expense_agent": ExpenseAgent(signature_service),
    }
    enforcer = PolicyEnforcer(settings)
    router = AgentRouter(tools=tools, enforcer=enforcer)
    aggregator = ResponseAggregator()
    state_store = SessionStateStore(session_ttl_minutes=settings.security.session_ttl_minutes)
    orchestrator = AgentOrchestrator(router=router, aggregator=aggregator, state_store=state_store, settings=settings)
    return orchestrator


@app.command()
def login(email: str, password: str) -> None:
    settings = get_settings()
    auth_service = AuthService(settings)
    try:
        token = auth_service.authenticate(email, password)
        console.print(f"Token: {token}")
    except ValueError as exc:
        console.print(f"[red]Authentication failed:[/red] {exc}")


@app.command()
def request(session_id: str, role: str, prompt: str) -> None:
    orchestrator = build_orchestrator()
    result = asyncio.run(orchestrator.handle_request(session_id=session_id, role=role, request=prompt))
    console.print(result)


if __name__ == "__main__":
    app()

