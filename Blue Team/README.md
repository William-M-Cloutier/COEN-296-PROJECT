# Blue Team AI Governance Project

A secure multi-agent system implementing MAESTRO framework defenses for AI governance.

## 🎯 Project Overview

This project implements a secure expense management system with AI agent orchestration, featuring:

- **MAESTRO Foundation Models Defense**: Hallucination detection and prevention
- **Agent Ecosystem Defense**: Signed communication between agents
- **RAG/Vector DB Integration**: Document management and policy retrieval
- **Multi-Agent Orchestration**: Intelligent task routing and workflow management

## 🏗️ Architecture

```
app/
├── agent.py           # Core Agent with orchestration and hallucination detection
├── expense_agent.py   # Specialized expense workflow agent
├── tools.py           # Mock DriveAPI and HRSystemAPI
├── main.py            # FastAPI application with endpoints
└── retriever.py       # RAG/knowledge base integration
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the server
uvicorn app.main:app --reload --port 8000
```

The application will be available at `http://localhost:8000`

## 📡 API Endpoints

### Core Endpoints

- `GET /health` - Health check endpoint
- `POST /tasks` - Submit tasks for agent orchestration
- `GET /logs` - Retrieve system event logs
- `GET /login` - Login page
- `GET /` - Main chat UI

### Agent Endpoints

- `POST /agents/email/send` - Signed agent email endpoint
  - Requires `signature` header with value `AGENT_SIG_SECRET`
  - Body: `{"to": "email", "subject": "subject", "body": "content"}`

### Red Team Testing

- `POST /tests/rt-01` - Hallucination detection test

## 🛡️ Security Features

### MAESTRO Defenses Implemented

1. **Foundation Models Defense**
   - Hallucination detection via keyword matching
   - Confidence scoring (threshold: 0.5)
   - Automatic blocking of suspicious prompts

2. **Agent Ecosystem Defense**
   - Signed communication between agents
   - Signature verification on agent endpoints
   - 403 Forbidden on invalid signatures

## 🔄 Expense Workflow

The expense agent implements a full workflow:

1. **Policy Retrieval**: Fetches expense policies via DriveAPI
2. **Approval Logic**: Approves expenses ≤ $100, denies others
3. **HR Integration**: Updates employee balances for approved expenses
4. **Audit Logging**: Records all actions to `logs/events.jsonl`

### Example Expense Request

```python
# Via Agent.handle_task()
result = agent.handle_task(
    task="Process expense reimbursement",
    data={
        "employee_id": "emp-001",
        "amount": 75.0,
        "request": "Business lunch with client"
    }
)
```

## 📊 Mock Data

### Employees
- `emp-001`: Alice Employee (Balance: $1200)
- `emp-002`: Bob Johnson (Balance: $500)
- `emp-003`: Charlie Smith (Balance: $750)

### Policies
- `policy_001.pdf`: Max Reimbursement is $100
- `hr_policy_002.pdf`: Standard Employee T&Cs

## 🧪 Testing Hallucination Detection

```python
from app import Agent

agent = Agent()

# Test with ambiguous input
result = agent.generate_with_verification("What is the capital of Atlantis?")
# Returns: flagged=True, confidence=0.2, hallucination_detected=True

# Test with normal input
result = agent.generate_with_verification("What is the expense policy?")
# Returns: flagged=False, confidence=0.9, hallucination_detected=False
```

## 📝 Logging

All events are logged to `logs/events.jsonl` in JSON Lines format:

```json
{"timestamp": "2024-11-19T...", "actor": "agent", "action": "hallucination_detection", "flagged": true}
{"timestamp": "2024-11-19T...", "actor": "expense_agent", "action": "task_complete", "decision": "Approved"}
```

## 🔧 Configuration

- **Log Directory**: `./logs/` (auto-created)
- **Agent Signature Secret**: `AGENT_SIG_SECRET`
- **Expense Policy Threshold**: $100

## 📚 API Classes

### Agent (Core Orchestrator)
- `plan(task, data)` - Generate execution plan
- `handle_task(task, data)` - Route and execute tasks
- `generate_with_verification(prompt)` - Hallucination detection

### ExpenseAgent
- `process_report(employee_id, amount, request)` - Full expense workflow

### DriveAPI (Mock)
- `search_file(query)` - Search document repository

### HRSystemAPI (Mock)
- `get_employee(employee_id)` - Retrieve employee profile
- `update_balance(employee_id, amount)` - Update reimbursement balance

## 🎓 MAESTRO Framework Compliance

This implementation addresses the following MAESTRO categories:

- **[M1] Foundation Models**: Hallucination detection with confidence scoring
- **[M6] Agent Ecosystem**: Signed agent communication
- **[M7] Orchestration**: Multi-agent task routing and workflow management

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is an academic project for AI governance demonstration purposes.

