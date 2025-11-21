# System User Guide
## Blue Team AI Governance - Enterprise Expense Management Copilot

**Version:** 1.0  
**Date:** November 2024  
**Sections:** 2, 11

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Expense Policies](#expense-policies)
3. [Request Format](#request-format)
4. [Usage Examples](#usage-examples)
5. [Expected Outputs](#expected-outputs)
6. [Security Features](#security-features)
7. [Troubleshooting](#troubleshooting)

---

## 1. System Overview

The Blue Team Enterprise Expense Management Copilot is an AI-powered system designed to process expense reimbursement requests with built-in security controls and policy enforcement.

**Key Features:**
- Automated expense policy retrieval
- Real-time approval/denial decisions
- HR system integration for reimbursements
- Email notifications
- Comprehensive audit logging

---

## 2. Expense Policies

### Current Policy
**Max Reimbursement: $100**

```
Policy Document: policy_001.pdf
Content: "Max Reimbursement is $100."
```

### Policy Rules
- Expenses **≤ $100.00**: Automatically approved
- Expenses **> $100.00**: Automatically denied
- All expenses require valid employee ID
- Reimbursement updates employee balance immediately

---

## 3. Request Format

### API Endpoint
```
POST /tasks
Content-Type: application/json
```

### Request Structure

#### For Expense Tasks:
```json
{
  "task": "process expense reimbursement",
  "user_role": "employee",
  "data": {
    "employee_id": "E420",
    "amount": 42.00,
    "request_content": "Taxis to client meeting"
  }
}
```

#### Field Descriptions:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task` | string | Yes | Task description containing "expense" or "reimbursement" |
| `user_role` | string | No | User role (default: "employee") |
| `data.employee_id` | string | Yes | Employee identifier (format: E###) |
| `data.amount` | float | Yes | Expense amount in USD |
| `data.request_content` | string | Yes | Description of expense |

---

## 4. Usage Examples

### Example 1: Successful Expense (Approved)

**Screenshot 1: API Request Body**
```
POST http://localhost:8000/tasks
Content-Type: application/json

{
  "task": "process expense reimbursement",
  "user_role": "employee",
  "data": {
    "employee_id": "E420",
    "amount": 75.00,
    "request_content": "Business lunch with client at Downtown Bistro"
  }
}
```

**Screenshot 2: API Response (Success)**
```json
{
  "status": "ok",
  "user_role": "employee",
  "result": {
    "orchestration": {
      "plan": [
        "analyze:expense",
        "route:expense_agent",
        "execute:expense_agent",
        "notify:employee"
      ],
      "steps_completed": [
        {
          "step": "analyze:expense",
          "status": "completed"
        },
        {
          "step": "route:expense_agent",
          "status": "completed",
          "target": "ExpenseAgent"
        },
        {
          "step": "execute:expense_agent",
          "status": "completed",
          "result": {
            "decision": "Approved",
            "policy_context": "Max Reimbursement is $100.",
            "reimbursement_amount": 75.00,
            "new_balance": 575.00,
            "employee_name": "Alice Smith"
          }
        },
        {
          "step": "notify:employee",
          "status": "completed",
          "notification": "Expense approved: $75.0 reimbursed to Alice Smith"
        }
      ]
    },
    "expense_result": {
      "decision": "Approved",
      "policy_context": "Max Reimbursement is $100.",
      "reimbursement_amount": 75.00,
      "new_balance": 575.00,
      "employee_name": "Alice Smith"
    },
    "notification": {
      "status": "Email notification sent",
      "message": "Expense approved: $75.0 reimbursed to Alice Smith"
    },
    "provenance": {
      "decision_id": "DEC-a7f3c2b1",
      "policy_context_id": "policy_001.pdf",
      "policy_content": "Max Reimbursement is $100.",
      "timestamp": "2024-11-19T10:30:45.123456Z",
      "agent": "expense_agent",
      "actions_taken": [
        "retrieved_policy",
        "validated_employee",
        "calculated_reimbursement",
        "updated_balance"
      ]
    }
  }
}
```

**Screenshot 3: Log Entry (events.jsonl)**
```json
{
  "timestamp": "2024-11-19T10:30:45.123456Z",
  "actor": "expense_agent",
  "action": "task_complete",
  "task": "process expense reimbursement",
  "decision": "Approved",
  "reimbursement_amount": 75.0,
  "notification": "Expense approved: $75.0 reimbursed to Alice Smith",
  "decision_id": "DEC-a7f3c2b1",
  "policy_context_id": "policy_001.pdf"
}
```

---

### Example 2: Denied Expense (Exceeds Policy)

**Screenshot 4: API Request Body**
```
POST http://localhost:8000/tasks
Content-Type: application/json

{
  "task": "process expense reimbursement",
  "user_role": "employee",
  "data": {
    "employee_id": "E421",
    "amount": 150.00,
    "request_content": "Conference registration fee"
  }
}
```

**Screenshot 5: API Response (Denied)**
```json
{
  "status": "ok",
  "user_role": "employee",
  "result": {
    "expense_result": {
      "decision": "Denied",
      "policy_context": "Max Reimbursement is $100.",
      "reimbursement_amount": 0.0,
      "reason": "Expense amount $150.0 exceeds policy limit ($100.00)"
    },
    "notification": {
      "status": "Email notification sent",
      "message": "Expense denied: Expense amount $150.0 exceeds policy limit ($100.00)"
    }
  }
}
```

---

## 5. Expected Outputs

### Approved Expense Output Structure

```json
{
  "status": "ok",
  "result": {
    "expense_result": {
      "decision": "Approved",
      "reimbursement_amount": <AMOUNT>,
      "new_balance": <NEW_BALANCE>,
      "employee_name": "<NAME>"
    },
    "provenance": {
      "decision_id": "DEC-<UNIQUE_ID>",
      "policy_context_id": "policy_001.pdf"
    }
  }
}
```

### Denied Expense Output Structure

```json
{
  "status": "ok",
  "result": {
    "expense_result": {
      "decision": "Denied",
      "reimbursement_amount": 0.0,
      "reason": "<DENIAL_REASON>"
    }
  }
}
```

---

## 6. Security Features

### Role-Based Access Control (RBAC)
- **Employee Role**: Can submit expense requests
- **Admin Role**: Can upload policies and manage system
- Upload operations require admin role (403 Forbidden for employees)

### Security Logs
All actions logged to `logs/events.jsonl`:
- Task submissions with user_role
- Access denied events
- Hallucination detection alerts
- Anomaly detection (high-value transactions)

### Provenance Tracking
Every expense decision includes:
- Unique decision ID
- Policy document used
- Timestamp
- Actions taken

---

## 7. Troubleshooting

### Common Issues

#### Issue 1: 403 Forbidden Error
**Symptom:** "Forbidden: Only admin users can upload policies"  
**Cause:** Employee user attempting admin-only action  
**Solution:** Use admin user_role for upload tasks

#### Issue 2: Employee Not Found
**Symptom:** Error in expense_result  
**Cause:** Invalid employee_id  
**Solution:** Use valid employee IDs: E420, E421, E422

#### Issue 3: Expense Denied
**Symptom:** Decision: "Denied"  
**Cause:** Amount exceeds $100 policy limit  
**Solution:** Submit expenses ≤ $100 or request policy update from admin

### Support

For additional support:
- Check `logs/events.jsonl` for detailed event logs
- Review `redteam/results/` for security test results
- Contact system administrator for policy updates

---

## Appendix: Available Employees

| Employee ID | Name | Initial Balance | Bank Account |
|-------------|------|-----------------|--------------|
| E420 | Alice Smith | $500.00 | 123456 |
| E421 | Bob Johnson | $750.00 | 789012 |
| E422 | Charlie Davis | $1000.00 | 345678 |

