#!/usr/bin/env python3
"""
MCP Server - Model Context Protocol Server
Dynamic message bus for agent-to-agent communication with protocol-based routing

This service runs separately from the main application on port 8001.
It provides secure, signed message passing between autonomous agents with
protocol selection for different task types.
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Server - Model Context Protocol",
    description="Dynamic message bus for agent communication with protocol-based routing",
    version="1.0.0"
)

# Mock signature secret for agent authentication (Agent Ecosystem Defense)
AGENT_SIG_SECRET = "MOCK_MCP_SECRET"

# In-memory message queue (global list)
MESSAGE_QUEUE: List[dict] = []


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


@app.post("/send")
async def send_message(
    message: AgentMessage,
    signature: Optional[str] = Header(None)
) -> dict:
    """
    Send a message to the message bus with protocol-based routing.
    
    Security: Requires valid signature header for authentication.
    Implements Agent Ecosystem defense: Signed communication between agents.
    
    Args:
        message: AgentMessage containing sender, recipient, protocol, task_id, payload
        signature: Authentication signature from request header
    
    Returns:
        Success response with message ID and protocol
    
    Raises:
        HTTPException 403: If signature is missing or invalid
    """
    # Agent Ecosystem Defense: Verify signature
    if signature is None or signature != AGENT_SIG_SECRET:
        logger.warning(
            f"[MCP Security] Unauthorized message attempt from {message.sender} "
            f"(protocol: {message.protocol})"
        )
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Missing or invalid agent signature"
        )
    
    # Create message record with protocol information
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

