# User Guide: Interacting with Blue Team AI Governance System

**Version:** 1.0  
**Date:** November 19, 2024  
**System:** Blue Team AI Governance - Enterprise Copilot

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Getting Started](#getting-started)
4. [User Roles](#user-roles)
5. [Submitting Tasks](#submitting-tasks)
6. [Expense Management](#expense-management)
7. [Admin Operations](#admin-operations)
8. [API Endpoints](#api-endpoints)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

The Blue Team AI Governance system is an AI-powered expense management platform with enterprise-grade security controls. This guide explains how to interact with the system as an employee or administrator.

### Key Features
- ✅ Secure expense reimbursement processing
- ✅ Role-based access control (RBAC)
- ✅ Automated policy enforcement
- ✅ Real-time anomaly detection
- ✅ Complete audit trail

---

## System Overview

### Architecture
The system consists of two main components:

1. **Main Application Server** (Port 8000)
   - Primary API endpoint for task submission
   - Core Agent orchestration
   - Security controls

2. **MCP Server** (Port 8001)
   - Message bus for agent communication
   - Inter-agent message routing
   - Signature validation

### User Interface
The system provides a RESTful API interface. You can interact with it using:
- Command-line tools (curl, httpie)
- API clients (Postman, Insomnia)
- Custom applications
- Web interface (if deployed)

---

## Getting Started

### Prerequisites
- Access to the system API endpoint
- Valid employee ID (for employees)
- Admin API key (for administrators)
- HTTP client or API tool

### Base URL
```
Main Application: http://localhost:8000
MCP Server: http://localhost:8001
```

### Authentication
- **Employees:** No authentication required for expense submissions
- **Administrators:** Require `X-Admin-Token` header with valid API key

---

## User Roles

### Employee Role
**Capabilities:**
- Submit expense reimbursement requests
- View expense status
- Check reimbursement balance

**Limitations:**
- Cannot upload policies
- Cannot access admin endpoints
- Cannot modify system settings

### Administrator Role
**Capabilities:**
- All employee capabilities
- Upload policy documents
- Access admin endpoints
- Run security tests
- View system logs

**Authentication:**
- Requires `X-Admin-Token: SECRET_123_ADMIN_KEY` header

---

## Submitting Tasks

### Task Submission Endpoint
```
POST http://localhost:8000/tasks
Content-Type: application/json
```

### Request Format
```json
{
  "task": "task_description",
  "user_role": "employee" | "admin",
  "data": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

### Response Format
```json
{
  "status": "ok" | "error",
  "user_role": "employee" | "admin",
  "authenticated_admin": true | false,
  "result": {
    // Task-specific result data
  }
}
```

---

## Expense Management

### Submitting an Expense Request

**Endpoint:** `POST /tasks`

**Request Example:**
```json
{
  "task": "process expense reimbursement",
  "user_role": "employee",
  "data": {
    "employee_id": "E420",
    "amount": 75.00,
    "request_content": "Business lunch with client"
  }
}
```

**Response Example:**
```json
{
  "status": "ok",
  "user_role": "employee",
  "authenticated_admin": false,
  "result": null
}
```

**Note:** The expense is processed asynchronously via MCP. Check the inbox to see the result.

### Checking Expense Status

**Endpoint:** `POST /agents/expense/check_inbox`

**Request:**
```bash
curl -X POST http://localhost:8000/agents/expense/check_inbox
```

**Response Example:**
```json
{
  "status": "ok",
  "message": "Processed 1 message(s) from inbox",
  "message_count": 1,
  "protocols_used": ["expense_task"],
  "results": [
    {
      "message_id": "MSG-0001",
      "task_id": "5303",
      "protocol": "expense_task",
      "status": "processed",
      "result": {
        "decision": "Approved",
        "policy_context": "Max Reimbursement is $100.",
        "reimbursement_amount": 75.0,
        "new_balance": 575.0,
        "employee_name": "Alice Smith"
      }
    }
  ]
}
```

### Expense Approval Criteria

**Policy:** Maximum reimbursement is $100.00 per expense

**Approval Rules:**
- ✅ Amount ≤ $100.00 → **Approved**
- ❌ Amount > $100.00 → **Denied**

**Examples:**
- $50.00 → ✅ Approved
- $100.00 → ✅ Approved (boundary)
- $150.00 → ❌ Denied (exceeds limit)

### Valid Employee IDs

The system recognizes the following employee IDs:
- **E420** - Alice Smith
- **E421** - Bob Johnson
- **E422** - Charlie Davis

**Note:** Any other employee ID will be rejected with an identity validation error.

---

## Admin Operations

### Uploading a Policy Document

**Endpoint:** `POST /tasks`  
**Authentication:** Required (X-Admin-Token header)

**Request Example:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: SECRET_123_ADMIN_KEY" \
  -d '{
    "task": "upload new policy document",
    "user_role": "admin",
    "data": {
      "policy_file": "updated_policy.pdf"
    }
  }'
```

**Response:**
```json
{
  "status": "ok",
  "user_role": "admin",
  "authenticated_admin": true,
  "result": {
    "orchestration": {
      "plan": [...],
      "steps_completed": [...]
    }
  }
}
```

**Error Response (No Token):**
```json
{
  "detail": "Unauthorized: Invalid or missing Admin Token. Provide X-Admin-Token header."
}
```

### Sending Email Notifications

**Endpoint:** `POST /agents/email/send`  
**Authentication:** Required (signature header)

**Request Example:**
```bash
curl -X POST http://localhost:8000/agents/email/send \
  -H "Content-Type: application/json" \
  -H "signature: AGENT_SIG_SECRET" \
  -d '{
    "to": "employee@company.com",
    "subject": "Expense Approved",
    "body": "Your expense has been approved and will be reimbursed."
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Email sent successfully to employee@company.com",
  "subject": "Expense Approved"
}
```

### Running Security Tests

**Endpoint:** `POST /tests/rt-full`

**Request:**
```bash
curl -X POST http://localhost:8000/tests/rt-full
```

**Response:**
```json
{
  "status": "ok",
  "message": "Full Red Team suite executed",
  "results": {
    "suite_name": "RT-FULL",
    "tests": [...],
    "summary": {
      "total_tests": 4,
      "passed": 4,
      "failed": 0
    }
  }
}
```

---

## API Endpoints

### Main Application Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/tasks` | POST | Optional* | Submit a task |
| `/agents/email/send` | POST | Required | Send email notification |
| `/agents/expense/check_inbox` | POST | None | Check expense agent inbox |
| `/tests/rt-full` | POST | None | Run Red Team test suite |

*Admin operations require X-Admin-Token header

### MCP Server Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/send` | POST | Required | Send message to agent |
| `/inbox/{recipient}` | GET | None | Retrieve messages for recipient |
| `/status` | GET | None | Health check |

---

## Examples

### Example 1: Submit Valid Expense

**Request:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "process expense reimbursement",
    "user_role": "employee",
    "data": {
      "employee_id": "E420",
      "amount": 42.00,
      "request_content": "Taxi to client meeting"
    }
  }'
```

**Expected Result:**
- Task submitted successfully
- Expense approved (amount ≤ $100)
- Balance updated: $500 → $542

---

### Example 2: Submit Expense Exceeding Limit

**Request:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "process expense reimbursement",
    "user_role": "employee",
    "data": {
      "employee_id": "E420",
      "amount": 150.00,
      "request_content": "Conference registration"
    }
  }'
```

**Expected Result:**
- Task submitted successfully
- Expense denied (amount > $100)
- Reason: "Expense amount $150.0 exceeds policy limit ($100.00)"

---

### Example 3: Admin Upload Policy

**Request:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: SECRET_123_ADMIN_KEY" \
  -d '{
    "task": "upload new expense policy",
    "user_role": "admin",
    "data": {
      "policy_file": "updated_policy_2024.pdf"
    }
  }'
```

**Expected Result:**
- Admin authenticated successfully
- Task processed
- Policy uploaded

---

### Example 4: Invalid Employee ID

**Request:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "process expense reimbursement",
    "user_role": "employee",
    "data": {
      "employee_id": "E999",
      "amount": 50.00,
      "request_content": "Test expense"
    }
  }'
```

**Expected Result:**
- Task submitted
- Identity validation failed
- Response: "Employee E999 not found in HR system"
- Status: denied

---

### Example 5: Missing Employee ID

**Request:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "process expense reimbursement",
    "user_role": "employee",
    "data": {
      "amount": 50.00,
      "request_content": "Missing employee ID"
    }
  }'
```

**Expected Result:**
- Task submitted
- Validation error
- Response: "Missing employee_id"
- Status: denied

---

## Troubleshooting

### Common Issues

#### Issue 1: "401 Unauthorized" when uploading policy
**Cause:** Missing or invalid admin token  
**Solution:** Include `X-Admin-Token: SECRET_123_ADMIN_KEY` header

#### Issue 2: "Employee not found in HR system"
**Cause:** Invalid employee ID  
**Solution:** Use valid employee ID (E420, E421, or E422)

#### Issue 3: "Missing employee_id"
**Cause:** Employee ID field not provided  
**Solution:** Include `employee_id` in the data payload

#### Issue 4: Expense denied - "exceeds policy limit"
**Cause:** Amount > $100.00  
**Solution:** Submit expense ≤ $100.00

#### Issue 5: "403 Forbidden" when sending email
**Cause:** Missing signature header  
**Solution:** Include `signature: AGENT_SIG_SECRET` header

#### Issue 6: Task submitted but no result
**Cause:** Expense processing is asynchronous  
**Solution:** Check inbox using `POST /agents/expense/check_inbox`

---

### Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | None |
| 401 | Unauthorized | Provide valid admin token |
| 403 | Forbidden | Provide valid signature |
| 500 | Server Error | Check server logs |

---

### Getting Help

**Log Files:**
- Security events: `logs/events.jsonl`
- Test results: `docs/e2e_test_results.json`
- Red Team results: `redteam/results/RT-FULL/rt-full-results.json`

**System Status:**
- Check MCP server: `GET http://localhost:8001/status`
- Check main app: `GET http://localhost:8000/docs` (if Swagger enabled)

---

## Best Practices

### For Employees

1. **Always include employee_id** in expense requests
2. **Keep amounts ≤ $100.00** to ensure approval
3. **Provide clear request_content** for audit purposes
4. **Check inbox** after submitting to see results
5. **Use valid employee IDs** (E420, E421, E422)

### For Administrators

1. **Always include X-Admin-Token** header for admin operations
2. **Keep admin token secure** - never share or commit to code
3. **Review security logs** regularly (`logs/events.jsonl`)
4. **Run security tests** periodically (`POST /tests/rt-full`)
5. **Monitor anomaly alerts** for suspicious activity

---

## Security Features

### Authentication
- Admin operations require API key
- Token validation enforced
- Unauthorized access blocked

### Identity Validation
- Employee IDs validated against HR system
- Fake IDs rejected
- Missing IDs detected

### Input Validation
- Required fields enforced
- Amount validation (positive values)
- Policy limits enforced

### Anomaly Detection
- High-value transactions flagged (>$5000)
- Security alerts logged
- Audit trail maintained

### Denylist Protection
- Dangerous commands blocked
- Financial manipulation prevented
- Unauthorized operations stopped

---

## Quick Reference

### Employee Expense Request
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "process expense reimbursement",
    "user_role": "employee",
    "data": {
      "employee_id": "E420",
      "amount": 50.00,
      "request_content": "Description"
    }
  }'
```

### Admin Upload
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: SECRET_123_ADMIN_KEY" \
  -d '{
    "task": "upload policy",
    "user_role": "admin",
    "data": {}
  }'
```

### Check Inbox
```bash
curl -X POST http://localhost:8000/agents/expense/check_inbox
```

---

## Appendix

### Employee Database

| Employee ID | Name | Initial Balance |
|------------|------|----------------|
| E420 | Alice Smith | $500.00 |
| E421 | Bob Johnson | $750.00 |
| E422 | Charlie Davis | $1000.00 |

### Policy Limits

- **Maximum Reimbursement:** $100.00 per expense
- **Anomaly Threshold:** $5,000.00 (flagged for review)
- **Policy Source:** `policy_001.pdf` - "Max Reimbursement is $100."

### Admin Credentials

- **API Key:** `SECRET_123_ADMIN_KEY`
- **Header Name:** `X-Admin-Token`
- **Email Signature:** `AGENT_SIG_SECRET`
- **MCP Signature:** `MOCK_MCP_SECRET`

---

**Document Version:** 1.0  
**Last Updated:** November 19, 2024  
**System Version:** 1.0.0

For additional support or questions, refer to the system documentation or contact the system administrator.

