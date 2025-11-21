"""
Blue Team AI Governance Project - Application Package

This package contains the core agent implementation with:
- Agent orchestration and routing
- Expense workflow management
- Hallucination detection (MAESTRO Foundation Models defense)
- Mock APIs for Drive and HR systems
"""

from .agent import Agent, build_orchestrator
from .tools import DriveAPI, HRSystemAPI
from .expense_agent import ExpenseAgent

__all__ = [
    'Agent',
    'build_orchestrator',
    'DriveAPI',
    'HRSystemAPI',
    'ExpenseAgent',
]

