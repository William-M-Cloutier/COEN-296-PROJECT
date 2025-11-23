#!/usr/bin/env python3
"""
MCP Server - Model Context Protocol Server (Production Enhanced)
Dynamic message bus for agent-to-agent communication with protocol-based routing

This service runs separately from the main application on port 8001.
It provides secure, signed message passing between autonomous agents with
protocol selection, HMAC signature verification, and payload validation.

Production Features:
- HMAC-SHA256 signature verification with nonce and timestamp
- Pydantic schema validation for all payloads
- Rate limiting per sender
- Enhanced audit logging
"""

from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel, ValidationError
from typing import Optional, List, Dict
from datetime import datetime, timezone
import logging
import os
import json
from pathlib import Path
from collections import defaultdict
import time

from dotenv import load_dotenv

# Import production security utilities
try:
    from .security import SecurityManager
    from .mcp_schemas import validate_mcp_payload
except ImportError:
    # Fallback for when running as standalone script
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from security import SecurityManager
    from mcp_schemas import validate_mcp_payload

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Server - Model Context Protocol (Production)",
    description="Secure message bus with HMAC signatures and payload validation",
    version="2.0.0"
)

# ⚠️ SECURITY-CRITICAL: HMAC Signature Verification
# MANDATORY HUMAN REVIEW REQUIRED before merge
# Changes to signature validation must be reviewed by security team

# Load MCP secret for HMAC signatures
MCP_SECRET = os.getenv("MCP_SIG_SECRET") or os.getenv("AGENT_SIG_SECRET")
if not MCP_SECRET:
    raise ValueError(
        "MCP_SIG_SECRET or AGENT_SIG_SECRET environment variable must be set. "
        "See .env.example for configuration instructions."
    )

# Initialize Security Manager (for HMAC verification)
# Use a dummy JWT secret since we only need MCP signing here
security_manager = SecurityManager(
    jwt_secret=os.getenv("JWT_SECRET_KEY", "dummy_jwt_secret_for_mcp_server"),
    mcp_secret=MCP_SECRET
)

# In-memory message queue (global list)
MESSAGE_QUEUE: List[dict] = []

# Rate limiting: Track requests per sender
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # max requests per window
sender_requests: Dict[str, List[float]] = defaultdict(list)

# Audit log path
LOG_DIR = Path("./logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
SECURITY_LOG = LOG_DIR / "mcp_security.jsonl"


class AgentMessage(BaseModel):
    """
    Message structure for agent-to-agent communication with protocol support.
    
    Fields:
        sender: Agent identifier sending the message
        recipient: Agent identifier receiving the message
        protocol: Communication protocol type (e.g., 'expense_task', 'retrieval_task')
        task_id: Unique task identifier for tracking
        payload: Message data/parameters
    """
    sender: str
    recipient: str
    protocol: str
    task_id: str
    payload: dict


def log_security_event(event: dict) -> None:
    """Write security event to dedicated security log."""
    with SECURITY_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def check_rate_limit(sender: str) -> bool:
    """
    Check if sender has exceeded rate limit.
    
    Args:
        sender: Sender identifier
        
    Returns:
        True if within rate limit, False if exceeded
    """
    current_time = time.time()
    
    # Remove requests outside the current window
    sender_requests[sender] = [
        req_time for req_time in sender_requests[sender]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check if limit exceeded
    if len(sender_requests[sender]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    # Record this request
    sender_requests[sender].append(current_time)
    return True


@app.post("/send")
async def send_message(
    message: AgentMessage,
    signature: Optional[str] = Header(None),
    x_nonce: Optional[str] = Header(None, alias="X-Nonce"),
    x_timestamp: Optional[str] = Header(None, alias="X-Timestamp")
) -> dict:
    """
    Send a message to the message bus with protocol-based routing.
    
    Security Features:
    - HMAC-SHA256 signature verification with nonce and timestamp
    - Pydantic payload validation per protocol
    - Rate limiting per sender
    - Comprehensive audit logging
    
    Args:
        message: AgentMessage containing sender, recipient, protocol, task_id, payload
        signature: HMAC signature from request header
        x_nonce: Random nonce for replay protection
        x_timestamp: Unix timestamp for signature expiration
    
    Returns:
        Success response with message ID and protocol
    
    Raises:
        HTTPException 401: If signature is missing, invalid, or expired
        HTTPException 400: If payload validation fails
        HTTPException 429: If rate limit exceeded
    """
    # Rate Limiting Check
    if not check_rate_limit(message.sender):
        logger.warning(
            f"[MCP Security] Rate limit exceeded for sender={message.sender}"
        )
        log_security_event({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "rate_limit_exceeded",
            "sender": message.sender,
            "protocol": message.protocol,
            "severity": "MEDIUM"
        })
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW}s"
        )
    
    # HMAC Signature Verification
    if not signature or not x_nonce or not x_timestamp:
        logger.warning(
            f"[MCP Security] Missing signature components from {message.sender}"
        )
        log_security_event({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "missing_signature",
            "sender": message.sender,
            "protocol": message.protocol,
            "severity": "HIGH"
        })
        raise HTTPException(
            status_code=401,
            detail="Missing signature, nonce, or timestamp headers"
        )
    
    # HMAC Signature Verification
    if not signature or not x_nonce or not x_timestamp:
        logger.warning(
            f"[MCP Security] Missing signature components from {message.sender}"
        )
        log_security_event({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "missing_signature",
            "sender": message.sender,
            "protocol": message.protocol,
            "severity": "HIGH"
        })
        raise HTTPException(
            status_code=401,
            detail="Missing signature, nonce, or timestamp headers"
        )
    
    try:
        # Convert timestamp to int
        timestamp_int = int(x_timestamp)
        
        # Verify HMAC signature with nonce and timestamp
        payload_dict = message.dict()
        security_manager.verify_mcp_signature(
            payload=payload_dict,
            signature=signature,
            nonce=x_nonce,
            timestamp=timestamp_int
        )
        
        logger.debug(
            f"[MCP Security] Signature verified for sender={message.sender}, "
            f"nonce={x_nonce}, timestamp={timestamp_int}"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions from verify_mcp_signature
        raise
    except Exception as e:
        logger.error(
            f"[MCP Security] Signature verification failed: {e}"
        )
        log_security_event({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "signature_verification_failed",
            "sender": message.sender,
            "protocol": message.protocol,
            "error": str(e),
            "severity": "HIGH"
        })
        raise HTTPException(
            status_code=401,
            detail=f"Signature verification failed: {str(e)}"
        )
    
    # Payload Validation (Pydantic Schema)
    try:
        validated_payload = validate_mcp_payload(message.protocol, message.payload)
        logger.info(
            f"[MCP Security] Payload validated for protocol={message.protocol}"
        )
    except ValidationError as e:
        logger.error(
            f"[MCP Security] Payload validation failed for {message.protocol}: {e}"
        )
        log_security_event({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "payload_validation_failed",
            "sender": message.sender,
            "protocol": message.protocol,
            "errors": e.errors(),
            "severity": "HIGH"
        })
        raise HTTPException(
            status_code=400,
            detail=f"Payload validation failed: {e.errors()}"
        )
    except ValueError as e:
        # Unknown protocol or no schema defined
        logger.warning(
            f"[MCP Security] Unknown protocol or no schema: {message.protocol}"
        )
        # Allow custom protocols without strict validation
        if message.protocol != "custom":
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    message_record = {
        "id": f"MSG-{len(MESSAGE_QUEUE) + 1:04d}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sender": message.sender,
        "recipient": message.recipient,
        "protocol": message.protocol,
        "task_id": message.task_id,
        "payload": message.payload,
        "status": "pending"
    }
    
    # Add to message queue
    MESSAGE_QUEUE.append(message_record)
    
    logger.info(
        f"[MCP] Message {message_record['id']} received: "
        f"{message.sender} -> {message.recipient} "
        f"(Protocol: {message.protocol}, Task: {message.task_id})"
    )
    
    return {
        "status": "success",
        "message": "Message queued successfully with protocol routing",
        "message_id": message_record["id"],
        "recipient": message.recipient,
        "protocol": message.protocol,
        "timestamp": message_record["timestamp"]
    }


@app.get("/inbox/{recipient}")
async def get_inbox(recipient: str) -> dict:
    """
    Retrieve all pending messages for a specific recipient with protocol info.
    
    This endpoint allows agents to check their "mailbox" for incoming tasks.
    Messages are removed from the queue once retrieved (inbox clearing).
    Returned messages include protocol information for proper routing.
    
    Args:
        recipient: Agent identifier to retrieve messages for
    
    Returns:
        Dictionary containing list of messages with protocols and count
    """
    global MESSAGE_QUEUE
    
    # Filter messages for this recipient
    recipient_messages = [
        msg for msg in MESSAGE_QUEUE 
        if msg["recipient"] == recipient and msg["status"] == "pending"
    ]
    
    # Remove retrieved messages from queue (mark as delivered)
    MESSAGE_QUEUE = [
        msg for msg in MESSAGE_QUEUE 
        if not (msg["recipient"] == recipient and msg["status"] == "pending")
    ]
    
    # Group messages by protocol for better observability
    protocols_used = set(msg["protocol"] for msg in recipient_messages)
    
    logger.info(
        f"[MCP] Inbox check for {recipient}: "
        f"{len(recipient_messages)} message(s) retrieved "
        f"(Protocols: {', '.join(protocols_used) if protocols_used else 'None'})"
    )
    
    return {
        "recipient": recipient,
        "message_count": len(recipient_messages),
        "protocols": list(protocols_used),
        "messages": recipient_messages,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/status")
async def health_check() -> dict:
    """
    Health check endpoint for MCP server with protocol statistics.
    
    Returns:
        Server status, statistics, and protocol distribution
    """
    pending_messages = [msg for msg in MESSAGE_QUEUE if msg["status"] == "pending"]
    
    # Count messages by protocol
    protocol_stats = {}
    for msg in pending_messages:
        protocol = msg.get("protocol", "unknown")
        protocol_stats[protocol] = protocol_stats.get(protocol, 0) + 1
    
    return {
        "status": "healthy",
        "service": "MCP Server - Model Context Protocol",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "statistics": {
            "total_messages": len(MESSAGE_QUEUE),
            "pending_messages": len(pending_messages),
            "protocol_distribution": protocol_stats
        }
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint with service information and protocol support."""
    return {
        "service": "MCP Server - Model Context Protocol",
        "version": "1.0.0",
        "description": "Dynamic message bus for agent communication with protocol-based routing",
        "features": [
            "Signed agent authentication",
            "Protocol-based message routing",
            "Task tracking and correlation",
            "Message queuing and delivery"
        ],
        "endpoints": {
            "send": "POST /send - Send a message with protocol (requires signature)",
            "inbox": "GET /inbox/{recipient} - Check mailbox with protocol info",
            "status": "GET /status - Health check with protocol statistics"
        },
        "supported_protocols": [
            "expense_task - Expense processing workflow",
            "retrieval_task - Document retrieval operations",
            "custom - Custom protocol support"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting MCP Server with Model Context Protocol on port 8001...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

