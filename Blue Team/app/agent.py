from __future__ import annotations

import json
import logging
import requests
import random
import uuid
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional

# Import mock APIs and ExpenseAgent
from .tools import DriveAPI, HRSystemAPI
from .expense_agent import ExpenseAgent

# Import production security utilities
from .security import SecurityManager

# ⚠️ SECURITY-CRITICAL: Agent Communication Security
# MANDATORY HUMAN REVIEW REQUIRED before merge
# Changes to agent signature handling must be reviewed by security team

# MCP Server configuration for Model Context Protocol
MCP_URL = os.getenv("MCP_URL", "http://localhost:8001")
MCP_SECRET = os.getenv("MCP_SIG_SECRET") or os.getenv("AGENT_SIG_SECRET")
if not MCP_SECRET:
    raise ValueError(
        "MCP_SIG_SECRET or AGENT_SIG_SECRET environment variable must be set. "
        "See .env.example for configuration instructions."
    )

# Initialize Security Manager for HMAC signing
# Use dummy JWT secret since we only need MCP signing in Agent
_security_manager = SecurityManager(
    jwt_secret=os.getenv("JWT_SECRET_KEY", "dummy_jwt_for_agent"),
    mcp_secret=MCP_SECRET
)

# Configure logging for hallucination detection

logger = logging.getLogger(__name__)


class Agent:
    """
    Core Agent class implementing MAESTRO Foundation Models defense and orchestration.
    
    Provides:
    - Hallucination prevention
    - Task planning and routing
    - Integration with specialized agents (ExpenseAgent)
    """
    
    def __init__(self, retriever: Optional[Any] = None):
        """
        Initialize the Agent with retriever and specialized agents.
        
        Args:
            retriever: Optional retriever instance for RAG/document retrieval
        """
        self.log_dir = Path("./logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.events_log = self.log_dir / "events.jsonl"
        
        # Store retriever - initialize default if not provided
        if retriever is None:
            from .retriever import Retriever
            self.retriever = Retriever()
            logger.info("Agent initialized with default Retriever")
        else:
            self.retriever = retriever
        
        # Agent Frameworks: Allow/Deny List for security controls
        self.DENY_LIST = ['system_shutdown', 'file_write', 'transfer_all_funds']
        
        # Model Context Protocol: Tool/Protocol Map for dynamic routing
        self.tool_map = {
            'expense': 'external_mcp',
            'retrieval': 'internal_tool'
        }
        
        # Instantiate mock APIs
        self.drive_api = DriveAPI()
        self.hr_api = HRSystemAPI()
        
        # Instantiate specialized agents
        self.expense_agent = ExpenseAgent(self.drive_api, self.hr_api)
        
        logger.info("Agent initialized with ExpenseAgent, mock APIs, MCP, and security controls")
    
    def generate_with_verification(self, prompt: str) -> dict:
        """
        Generate response with hallucination detection.
        
        Implements MAESTRO Foundation Models defense:
        - Detects ambiguous/hallucination-prone keywords
        - Applies confidence threshold (< 0.5)
        - Flags potential hallucinations
        
        Args:
            prompt: The input prompt to verify
            
        Returns:
            dict with keys: output, flagged, confidence, hallucination_detected
        """
        # Check for known ambiguous words that trigger hallucination flags
        ambiguous_keywords = ['atlantis', 'fake study', 'perpetual motion']
        prompt_lower = prompt.lower()
        
        # Determine if prompt contains ambiguous content
        flagged = any(keyword in prompt_lower for keyword in ambiguous_keywords)
        
        # Simulate confidence scoring
        # If flagged, set confidence to 0.2 (low confidence)
        # Otherwise, set confidence to 0.9 (high confidence)
        if flagged:
            confidence = 0.2
        else:
            confidence = 0.9
        
        # Hallucination detection logic:
        # flagged OR confidence < 0.5 indicates hallucination
        hallucination_detected = flagged or confidence < 0.5
        
        # Log the hallucination detection event
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": "agent",
            "action": "hallucination_detection",
            "prompt": prompt,
            "flagged": flagged,
            "confidence": confidence,
            "hallucination_detected": hallucination_detected
        }
        
        # Write to events log
        self._write_event(log_entry)
        
        # Log to standard logger as well
        logger.info(
            f"Hallucination detection: flagged={flagged}, confidence={confidence}, "
            f"hallucination_detected={hallucination_detected}"
        )
        
        # Generate simulated output
        if hallucination_detected:
            output = "[BLOCKED: Potential hallucination detected]"
        else:
            output = "[SIMULATED OUTPUT: Safe response]"
        
        return {
            "output": output,
            "flagged": flagged,
            "confidence": confidence,
            "hallucination_detected": hallucination_detected
        }
    
    def _write_event(self, event: dict) -> None:
        """Write an event to the events.jsonl log file."""
        with self.events_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    
    def send_mcp_message(
        self, 
        recipient: str, 
        payload: dict, 
        task_id: str, 
        protocol: str
    ) -> dict:
        """
        Send a message to another agent via the external MCP Server.
        
        Implements Model Context Protocol with dynamic protocol selection.
        Implements Agent Ecosystem defense: HMAC-signed communication between agents.
        
        Production Security Features:
        - HMAC-SHA256 signature with nonce and timestamp
        - Replay attack protection (5-minute window)
        - Message integrity validation
        
        Args:
            recipient: Target agent identifier (e.g., 'ExpenseAgent')
            payload: Message data to send to recipient
            task_id: Unique task identifier for tracking
            protocol: Communication protocol type (e.g., 'expense_task', 'retrieval_task')
            
        Returns:
            Response from MCP server or error dict
        """
        message_data = {
            "sender": "CoreAgent",
            "recipient": recipient,
            "protocol": protocol,
            "task_id": task_id,
            "payload": payload
        }
        
        # Generate HMAC signature with nonce and timestamp
        mcp_signature = _security_manager.create_mcp_signature(message_data)
        
        headers = {
            "Content-Type": "application/json",
            "signature": mcp_signature.signature,
            "X-Nonce": mcp_signature.nonce,
            "X-Timestamp": str(mcp_signature.timestamp)
        }
        
        try:
            logger.info(
                f"[MCP] Sending HMAC-signed message to {recipient} "
                f"(Protocol: {protocol}, Task: {task_id}, Nonce: {mcp_signature.nonce})"
            )
            response = requests.post(
                f"{MCP_URL}/send",
                json=message_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(
                    f"[MCP] Message successfully sent to {recipient} "
                    f"(Protocol: {protocol})"
                )
                self._write_event({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "actor": "core_agent",
                    "action": "mcp_message_sent",
                    "recipient": recipient,
                    "protocol": protocol,
                    "task_id": task_id,
                    "nonce": mcp_signature.nonce,
                    "status": "success",
                    "security_method": "HMAC-SHA256"
                })
                return response.json()
            else:
                logger.error(
                    f"[MCP] Failed to send message: {response.status_code}"
                )
                return {
                    "status": "error",
                    "message": f"MCP server returned {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            logger.error("[MCP] Connection error: MCP server not available")
            self._write_event({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "core_agent",
                "action": "mcp_connection_error",
                "recipient": recipient,
                "protocol": protocol,
                "task_id": task_id,
                "error": "MCP server not available"
            })
            return {
                "status": "error",
                "message": "MCP server not available - will use direct call fallback"
            }
        except Exception as e:
            logger.error(f"[MCP] Unexpected error: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    def plan(self, task: str, data: dict) -> list[str]:
        """
        Plan the execution steps for a given task (Planner mechanism with MCP).
        
        Implements Model Context Protocol with dynamic protocol selection:
        - LLM Planner selects appropriate protocol based on task type
        - external_mcp protocol for expense tasks (message bus routing)
        - internal_tool protocol for retrieval tasks (direct internal calls)
        - Deny list checking for blocked actions
        
        Args:
            task: Task description
            data: Task data dictionary
            
        Returns:
            List of execution steps with protocol selection (may be blocked if deny-listed)
        """
        task_lower = task.lower()
        
        # Model Context Protocol: Dynamic Protocol Selection by LLM Planner
        if 'expense' in task_lower or 'reimbursement' in task_lower:
            # LLM selects external_mcp protocol for expense tasks
            protocol = self.tool_map['expense']
            plan = [
                'analyze:expense',
                'protocol:mcp_send',  # Protocol step for MCP routing
                'execute:expense_agent_wait',  # Wait for async MCP response
                'notify:employee'
            ]
            logger.info(
                f"[Planner] Created expense workflow plan with {protocol} protocol: {plan}"
            )
        elif 'retrieve' in task_lower or 'deploy' in task_lower:
            # LLM selects internal_tool protocol for retrieval tasks
            protocol = self.tool_map['retrieval']
            plan = [
                f"analyze:{task}",
                'tool:retriever_call',  # Protocol step for internal tool
                'execute:internal_class'
            ]
            logger.info(
                f"[Planner] Created retrieval plan with {protocol} protocol: {plan}"
            )
        else:
            # Default plan for other tasks (internal)
            protocol = 'internal_tool'
            plan = [
                f"analyze:{task}",
                f"retrieve_context:{task}",
                f"decide:{task}"
            ]
            logger.info(
                f"[Planner] Created general workflow plan with {protocol} protocol: {plan}"
            )
        
        # Agent Frameworks: Deny List Check
        # Iterate through plan steps and check for deny-listed keywords
        for step in plan:
            step_lower = step.lower()
            for denied_action in self.DENY_LIST:
                if denied_action in step_lower:
                    # Log high-risk event
                    logger.error(f"[SECURITY] Deny-listed action detected: {denied_action} in step {step}")
                    self._write_event({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "actor": "security",
                        "action": "denylisted_action_blocked",
                        "severity": "HIGH",
                        "blocked_action": denied_action,
                        "original_plan": plan,
                        "task": task
                    })
                    
                    # Replace plan with security block
                    plan = ['security_blocked:denylisted_action']
                    logger.warning(f"[SECURITY] Plan blocked and replaced: {plan}")
                    return plan
        
        # Also check the task itself for deny-listed keywords
        for denied_action in self.DENY_LIST:
            if denied_action in task_lower:
                logger.error(f"[SECURITY] Deny-listed action detected in task: {denied_action}")
                self._write_event({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "actor": "security",
                    "action": "denylisted_action_blocked",
                    "severity": "HIGH",
                    "blocked_action": denied_action,
                    "task": task
                })
                
                plan = ['security_blocked:denylisted_action']
                logger.warning(f"[SECURITY] Task blocked due to deny list: {plan}")
                return plan
        
        return plan
    
    def handle_task(self, task: str, data: dict) -> dict:
        """
        Handle a task by routing to appropriate agent (Agent Routing).
        
        Implements orchestration with specialized agent routing:
        - Expense tasks route to ExpenseAgent
        - Other tasks use simulation logic
        - Anomaly detection for high-value requests
        - Provenance tracking for decisions
        
        Expected input data for expense tasks:
        {'employee_id': 'E420', 'amount': 150.00, 'request_content': 'Taxis to client meeting.'}
        
        Args:
            task: Task description
            data: Task data dictionary
            
        Returns:
            Aggregated result dictionary with orchestration steps and agent results
        """
        # Evaluation & Observability: Anomaly Detection
        # Check for high-value transactions (> $5000)
        amount = data.get('amount', 0.0)
        if amount > 5000.00:
            logger.error(f"[ANOMALY] High-value request detected: ${amount}")
            self._write_event({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "anomaly_detector",
                "action": "ANOMALY_HIGH_VALUE_REQUEST",
                "severity": "HIGH",
                "amount": amount,
                "task": task,
                "employee_id": data.get('employee_id', 'unknown')
            })
        
        # Generate execution plan
        plan = self.plan(task, data)
        
        # Log task start
        self._write_event({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": "agent",
            "action": "task_start",
            "task": task,
            "plan": plan
        })
        
        # Route based on plan - Model Context Protocol implementation
        if 'protocol:mcp_send' in plan:
            logger.info("[Agent Routing] Using external_mcp protocol - routing via MCP")
            
            # Extract required fields for expense processing
            employee_id = data.get('employee_id')
            amount = data.get('amount', 0.0)
            request_content = data.get('request_content', task)
            
            # Identity Validation: Verify employee_id against HR system
            # This prevents unauthorized access and identity spoofing
            if not employee_id:
                logger.error("[Identity] Missing employee_id in expense request")
                self._write_event({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "actor": "identity_validator",
                    "action": "SECURITY_ALERT_MISSING_EMPLOYEE_ID",
                    "severity": "HIGH",
                    "task": task,
                    "reason": "Employee ID required for financial transactions"
                })
                return {
                    'status': 'denied',
                    'error': 'Missing employee_id',
                    'reason': 'Employee ID is required for expense processing',
                    'security_check': 'IDENTITY_VALIDATION_FAILED'
                }
            
            # Validate employee exists in HR system
            employee_profile = self.hr_api.get_profile(employee_id)
            if employee_profile is None:
                logger.error(f"[Identity] Invalid employee_id: {employee_id} not found in HR system")
                self._write_event({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "actor": "identity_validator",
                    "action": "SECURITY_ALERT_INVALID_EMPLOYEE_ID",
                    "severity": "HIGH",
                    "employee_id": employee_id,
                    "task": task,
                    "reason": "Employee ID not found in HR system"
                })
                return {
                    'status': 'denied',
                    'error': 'Invalid employee_id',
                    'reason': f'Employee {employee_id} not found in HR system',
                    'security_check': 'IDENTITY_VALIDATION_FAILED'
                }
            
            logger.info(
                f"[Identity] Employee validated: {employee_id} ({employee_profile.get('full_name')})"
            )
            logger.info(
                f"[MCP Routing] Processing expense: employee={employee_id}, "
                f"amount=${amount}, request={request_content}"
            )
            
            # Generate unique task ID for tracking
            task_id = str(random.randint(1000, 9999))
            
            # Send message via MCP with expense_task protocol
            mcp_response = self.send_mcp_message(
                recipient='ExpenseAgent',
                payload={
                    'employee_id': employee_id,
                    'amount': amount,
                    'request_content': request_content
                },
                task_id=task_id,
                protocol='expense_task'
            )
            
            # Check if MCP message was sent successfully
            if mcp_response.get('status') == 'error':
                logger.warning("[MCP Routing] MCP unavailable, using direct call fallback")
                # Fallback to direct call if MCP server is down
                expense_result = self.expense_agent.process_report(
                    employee_id=employee_id,
                    expense_amount=amount,
                    request_content=request_content
                )
            else:
                # Message successfully queued in MCP
                # For demo: still call agent directly to get result
                # In production: would wait for response message from MCP
                logger.info("[MCP Routing] Message queued in MCP, processing for demo")
                expense_result = self.expense_agent.process_report(
                    employee_id=employee_id,
                    expense_amount=amount,
                    request_content=request_content
                )
                # Add MCP metadata to result
                expense_result['mcp_metadata'] = {
                    'task_id': task_id,
                    'message_id': mcp_response.get('message_id'),
                    'protocol': 'expense_task',
                    'routing': 'external_mcp'
                }
        elif 'execute:internal_class' in plan:
            logger.info("[Agent Routing] Using internal_tool protocol")
            
            # Call internal retriever
            if self.retriever:
                retrieval_result = self.retriever.get_context(task)
                logger.info(f"[Internal Tool] Retrieved context: {retrieval_result}")
                
                return {
                    'orchestration': {
                        'plan': plan,
                        'protocol': 'internal_tool',
                        'steps_completed': [
                            {'step': plan[0], 'status': 'completed'},
                            {'step': 'tool:retriever_call', 'status': 'completed'},
                            {'step': 'execute:internal_class', 'status': 'completed'}
                        ]
                    },
                    'task': task,
                    'retrieval': retrieval_result,
                    'response': 'Retrieval completed via internal tool',
                    'status': 'completed'
                }
            else:
                # Retriever not available
                return {
                    'orchestration': {
                        'plan': plan,
                        'protocol': 'internal_tool',
                        'steps_completed': []
                    },
                    'error': 'Retriever not initialized',
                    'status': 'error'
                }
        elif 'execute:expense_agent' in plan:
            # Legacy direct call support (backward compatibility)
            logger.info("[Agent Routing] Using legacy direct call to ExpenseAgent")
            
            employee_id = data.get('employee_id', 'unknown')
            amount = data.get('amount', 0.0)
            request_content = data.get('request_content', task)
            
            expense_result = self.expense_agent.process_report(
                employee_id=employee_id,
                expense_amount=amount,
                request_content=request_content
            )
            
            # Mock notification step (Email API Integration)
            notification_status = "Email notification sent"
            if expense_result['decision'] == 'Approved':
                notification_message = (
                    f"Expense approved: ${expense_result['reimbursement_amount']} "
                    f"reimbursed to {expense_result.get('employee_name', employee_id)}"
                )
            else:
                notification_message = (
                    f"Expense denied: {expense_result.get('reason', 'Exceeds policy limit')}"
                )
            
            logger.info(f"[Agent Routing] {notification_status}: {notification_message}")
            
            # Evaluation & Observability: Provenance Tracking
            # Generate unique decision ID
            import uuid
            decision_id = f"DEC-{uuid.uuid4().hex[:8]}"
            
            # Extract policy context ID from expense result
            policy_context = expense_result.get('policy_context', 'Max Reimbursement is $100.')
            policy_context_id = 'policy_001.pdf'  # Mock policy ID from DriveAPI
            
            # Build detailed provenance information
            provenance = {
                'decision_id': decision_id,
                'policy_context_id': policy_context_id,
                'policy_content': policy_context,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'agent': 'expense_agent',
                'actions_taken': [
                    'retrieved_policy',
                    'validated_employee',
                    'calculated_reimbursement',
                    'updated_balance' if expense_result['decision'] == 'Approved' else 'denied_request'
                ]
            }
            
            # Aggregate orchestration steps and expense agent result
            aggregated_result = {
                'orchestration': {
                    'plan': plan,
                    'steps_completed': [
                        {'step': 'analyze:expense', 'status': 'completed'},
                        {'step': 'route:expense_agent', 'status': 'completed', 'target': 'ExpenseAgent'},
                        {'step': 'execute:expense_agent', 'status': 'completed', 'result': expense_result},
                        {'step': 'notify:employee', 'status': 'completed', 'notification': notification_message}
                    ]
                },
                'expense_result': expense_result,
                'notification': {
                    'status': notification_status,
                    'message': notification_message
                },
                'provenance': provenance
            }
            
            # Log completion with provenance
            self._write_event({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "expense_agent",
                "action": "task_complete",
                "task": task,
                "decision": expense_result.get('decision'),
                "reimbursement_amount": expense_result.get('reimbursement_amount'),
                "notification": notification_message,
                "decision_id": provenance['decision_id'],
                "policy_context_id": provenance['policy_context_id']
            })
            
            return aggregated_result
        
        elif 'security_blocked:denylisted_action' in plan:
            # Handle security-blocked tasks (deny list)
            logger.warning("[Agent Routing] Task blocked by security deny list")
            
            result = {
                'orchestration': {
                    'plan': plan,
                    'steps_completed': [
                        {'step': 'security_blocked:denylisted_action', 'status': 'blocked', 'reason': 'Deny-listed action detected'}
                    ]
                },
                'task': task,
                'data': data,
                'response': 'Task blocked due to security policy: deny-listed action',
                'status': 'blocked',
                'error': 'Security violation: Task contains deny-listed action'
            }
            
            self._write_event({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "agent",
                "action": "task_blocked",
                "task": task,
                "handler": "security_deny_list"
            })
            
            return result
        
        else:
            # Fallback: simulation logic for non-expense tasks
            logger.info("[Agent Routing] Using simulation handler for general task")
            
            # Simple mock response
            result = {
                'orchestration': {
                    'plan': plan,
                    'steps_completed': [
                        {'step': plan[0], 'status': 'completed'},
                        {'step': plan[1], 'status': 'completed'} if len(plan) > 1 else None,
                        {'step': plan[2], 'status': 'completed'} if len(plan) > 2 else None
                    ]
                },
                'task': task,
                'data': data,
                'response': 'Simulation response for non-expense task',
                'status': 'completed'
            }
            
            # Remove None entries
            result['orchestration']['steps_completed'] = [
                step for step in result['orchestration']['steps_completed'] if step is not None
            ]
            
            # If retriever is available, could use it here
            if self.retriever:
                result['retrieval'] = 'Retriever would be used for context'
            
            # Log completion
            self._write_event({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "agent",
                "action": "task_complete",
                "task": task,
                "handler": "simulation"
            })
            
            return result


def build_orchestrator():
    """Starter-style helper to construct the orchestrator."""
    return Agent()


