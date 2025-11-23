# Final Architecture Diagram
## Blue Team Enterprise Copilot - System Architecture

**Version:** 1.0  
**Date:** November 2024  
**Section:** 11

---

## Architecture Overview

The Blue Team Enterprise Copilot implements a layered architecture with MAESTRO security controls integrated at multiple levels. The system processes expense reimbursement requests through a secure, orchestrated workflow.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                          │
│                        (FastAPI Endpoints)                            │
│                                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ POST /tasks │  │ POST /agents │  │ POST /tests/rt-full     │  │
│  │   (RBAC)    │  │ /email/send  │  │  (Red Team Testing)     │  │
│  │             │  │  (Signed)    │  │                         │  │
│  └──────┬──────┘  └──────────────┘  └─────────────────────────┘  │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CORE AGENT LAYER                              │
│                      (Orchestrator + Security)                       │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Core Agent (agent.py)                       │  │
│  │                                                                │  │
│  │  [MAESTRO: Foundation Models Defense]                         │  │
│  │  • Hallucination Detection (generate_with_verification)       │  │
│  │  • Confidence Scoring (threshold: 0.5)                        │  │
│  │  • Ambiguous keyword blocking                                 │  │
│  │                                                                │  │
│  │  [MAESTRO: Agent Frameworks Defense]                          │  │
│  │  • Deny List: [system_shutdown, file_write,                  │  │
│  │                 transfer_all_funds]                           │  │
│  │  • Plan Interception & Blocking                               │  │
│  │                                                                │  │
│  │  [MAESTRO: Evaluation & Observability]                        │  │
│  │  • Anomaly Detection (amount > $5000)                         │  │
│  │  • Provenance Tracking (decision_id, policy_context_id)      │  │
│  │  • Action Logs to events.jsonl                                │  │
│  │                                                                │  │
│  │  ┌──────────────────────────────────────────────────────┐    │  │
│  │  │          Planner (plan method)                        │    │  │
│  │  │  • Task Analysis                                      │    │  │
│  │  │  • Route Determination                                │    │  │
│  │  │  • Security Checks (Deny List)                        │    │  │
│  │  └────────────────┬─────────────────────────────────────┘    │  │
│  │                   │                                            │  │
│  │                   ▼                                            │  │
│  │  ┌──────────────────────────────────────────────────────┐    │  │
│  │  │       Agent Router (handle_task method)               │    │  │
│  │  │  • Anomaly Detection                                  │    │  │
│  │  │  • Task Routing                                       │    │  │
│  │  │  • Result Aggregation                                 │    │  │
│  │  └────────────────┬─────────────────────────────────────┘    │  │
│  └────────────────────┼──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SPECIALIZED AGENTS LAYER                          │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │           Expense Agent (expense_agent.py)                   │   │
│  │                                                              │   │
│  │  Workflow Steps:                                            │   │
│  │  1. Policy Retrieval    ──────────┐                        │   │
│  │  2. Report Review                  │                        │   │
│  │  3. Reimbursement Processing       │                        │   │
│  │                                    │                        │   │
│  └────────────────────────────────────┼────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────┐
         │                               │                           │
         ▼                               ▼                           ▼
┌──────────────────┐          ┌──────────────────┐        ┌──────────────────┐
│   DRIVE API      │          │  HR SYSTEM API   │        │   EMAIL API      │
│   (tools.py)     │          │   (tools.py)     │        │  (Notification)  │
│                  │          │                  │        │                  │
│ [MAESTRO: Data   │          │ [MAESTRO: Data   │        │                  │
│  Operations]     │          │  Operations]     │        │                  │
│                  │          │                  │        │                  │
│ • RAG/Vector DB  │          │ • Employee       │        │ • Mock Email     │
│   Mock           │          │   Profiles       │        │   Sending        │
│ • Document Store │          │ • Financial      │        │ • Success/Denial │
│   (search_file)  │          │   Information    │        │   Notifications  │
│ • Policy Upload  │          │ • Balance        │        │                  │
│   (upload_file)  │          │   Updates        │        │                  │
│                  │          │   (update_bal.)  │        │                  │
│ Provenance:      │          │                  │        │                  │
│ • source_id      │          │ Profile Fields:  │        │                  │
│ • timestamp      │          │ • full_name      │        │                  │
│ • sanitized flag │          │ • bank_account   │        │                  │
│                  │          │ • balance        │        │                  │
└──────────────────┘          └──────────────────┘        └──────────────────┘
```

---

## Data Flow: Successful Expense Request

```
1. User → POST /tasks
   ├─ Request: {task, user_role, data}
   └─ RBAC Check (main.py)
       └─ ✓ Authorized

2. Core Agent → plan()
   ├─ Analyze task: "expense reimbursement"
   ├─ Check deny list: ✓ No blocked keywords
   └─ Generate plan: [analyze, route, execute, notify]

3. Core Agent → handle_task()
   ├─ Anomaly Detection: $75 < $5000 ✓ OK
   └─ Route to: ExpenseAgent

4. ExpenseAgent → process_report()
   ├─ Step 1: DriveAPI.search_file('policy')
   │   └─ Returns: "Max Reimbursement is $100."
   ├─ Step 2: Decision Logic
   │   └─ $75 ≤ $100 → Approved
   └─ Step 3: HR Integration
       ├─ HRSystemAPI.get_profile('E420')
       │   └─ Returns: {full_name, bank_account_id, balance}
       └─ HRSystemAPI.update_balance('E420', 75.00)
           └─ New balance: $575.00

5. Core Agent → Aggregate Results
   ├─ Add provenance metadata
   │   ├─ decision_id: "DEC-a7f3c2b1"
   │   └─ policy_context_id: "policy_001.pdf"
   ├─ Generate notification
   └─ Log to events.jsonl

6. Response → User
   └─ {status: "ok", result: {...}}
```

---

## MAESTRO Security Layers Mapping

| MAESTRO Layer | Implementation | Location | Defense Type |
|---------------|----------------|----------|--------------|
| **M1: Foundation Models** | Hallucination Detection | agent.py | Confidence scoring, keyword blocking |
| **M6: Agent Frameworks** | Deny List | agent.py | Plan interception, action blocking |
| **M7: Security & Compliance** | RBAC | main.py | Role-based access control |
| **M8: Evaluation & Observability** | Anomaly Detection | agent.py | High-value transaction alerts |
| **M8: Evaluation & Observability** | Provenance Tracking | agent.py | Decision IDs, policy context |
| **M9: Data Operations** | Data Provenance | retriever.py | source_id, timestamp, sanitized |

---

## Deployment Architecture

```
Production Environment:
┌────────────────────────────────────────┐
│         Load Balancer / Gateway         │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│      FastAPI Application Server         │
│      (uvicorn app.main:app)            │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Core Agent + Security Layer    │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Specialized Agents Layer       │  │
│  └──────────────────────────────────┘  │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│         External Systems                │
│  • Vector DB / RAG (Mock: Drive API)  │
│  • HR System (Mock: HR API)           │
│  • Email Service (Mock: Notification) │
└────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│         Logging & Monitoring            │
│  • events.jsonl (Audit Log)           │
│  • Red Team Results (Security Tests)  │
└────────────────────────────────────────┘
```

---

## Component Details

### Core Agent (agent.py)
**Responsibilities:**
- Task orchestration and planning
- Security control enforcement
- Multi-agent coordination
- Anomaly detection
- Provenance tracking

**Key Methods:**
- `generate_with_verification()` - Hallucination detection
- `plan()` - Task planning with deny list checks
- `handle_task()` - Task routing and execution
- `_write_event()` - Event logging

### Expense Agent (expense_agent.py)
**Responsibilities:**
- Policy retrieval from DriveAPI
- Expense approval/denial logic
- HR system integration
- Balance updates

**Workflow:**
1. Retrieve policy → 2. Apply decision logic → 3. Update balance

### External APIs (tools.py)

**DriveAPI:**
- Mock vector database / RAG system
- Document storage and retrieval
- Policy management

**HRSystemAPI:**
- Employee profile management
- Financial balance tracking
- Reimbursement processing

---

## Security Architecture Summary

The architecture implements defense-in-depth with security controls at every layer:

- **API Layer:** RBAC, signature verification
- **Agent Layer:** Hallucination detection, deny lists, anomaly detection
- **Data Layer:** Provenance tracking, sanitization flags
- **Logging Layer:** Comprehensive audit trails

All security controls map to MAESTRO framework requirements and are validated through Red Team testing (RT-02, RT-03, RT-04, RT-05).

