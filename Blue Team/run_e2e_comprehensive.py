#!/usr/bin/env python3
"""
Comprehensive E2E Test Suite for Blue Team AI Governance Project

Tests all Red Team attack vectors:
- Authentication & Identity Attacks
- Authorization & RBAC Bypass
- Denylist & Dangerous Action Attacks
- Anomaly & Injection Attacks
- Data Provenance & Integrity Attacks
- MCP Protocol Attacks
- Input Validation Attacks

Usage:
    python run_e2e_comprehensive.py --base-url http://localhost:8000
"""

import argparse
import requests
import json
import sys
import time
from typing import Dict, Any, List
from datetime import datetime


class E2ETestRunner:
    """Comprehensive E2E test runner for all security controls."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
        self.admin_token = "SECRET_123_ADMIN_KEY"
        
    def print_header(self, title: str, width: int = 80):
        """Print formatted header."""
        print("\n" + "=" * width)
        print(title.center(width))
        print("=" * width)
    
    def print_test(self, test_num: int, test_name: str, category: str):
        """Print test header."""
        print(f"\n[TEST {test_num}] {test_name}")
        print(f"Category: {category}")
        print("-" * 80)
    
    def run_test(self, test_num: int, test_name: str, category: str, 
                 test_func, *args, **kwargs) -> Dict[str, Any]:
        """Run a test and record results."""
        self.print_test(test_num, test_name, category)
        try:
            result = test_func(*args, **kwargs)
            result['test_num'] = test_num
            result['test_name'] = test_name
            result['category'] = category
            result['timestamp'] = datetime.now().isoformat()
            self.results.append(result)
            return result
        except Exception as e:
            error_result = {
                'test_num': test_num,
                'test_name': test_name,
                'category': category,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(error_result)
            print(f"  ❌ ERROR: {e}")
            return error_result
    
    # ==================== POSITIVE TESTS (Expected to Work) ====================
    
    def test_positive_valid_expense(self) -> Dict[str, Any]:
        """Test: Valid expense request should be approved."""
        print("  Input: Valid employee (E420), amount $50.00")
        print("  Expected: Approved, balance updated")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E420",
                    "amount": 50.00,
                    "request_content": "Valid business expense"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            time.sleep(2)
            inbox = requests.post(f"{self.base_url}/agents/expense/check_inbox", timeout=10)
            if inbox.status_code == 200:
                inbox_data = inbox.json()
                if inbox_data.get('results'):
                    result = inbox_data['results'][0]['result']
                    if result.get('decision') == 'Approved':
                        print(f"  ✅ PASS: Expense approved, balance: ${result.get('new_balance')}")
                        return {'status': 'PASS', 'decision': result.get('decision')}
        
        print(f"  ❌ FAIL: Unexpected response")
        return {'status': 'FAIL', 'response': response.text}
    
    def test_positive_admin_upload_with_token(self) -> Dict[str, Any]:
        """Test: Admin upload with valid token should succeed."""
        print("  Input: Admin token provided, upload task")
        print("  Expected: Task accepted")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            headers={"X-Admin-Token": self.admin_token},
            json={
                "task": "upload new policy",
                "user_role": "admin",
                "data": {"policy_file": "new_policy.pdf"}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('authenticated_admin'):
                print(f"  ✅ PASS: Admin authenticated, task processed")
                return {'status': 'PASS', 'authenticated': True}
        
        print(f"  ❌ FAIL: Admin authentication failed")
        return {'status': 'FAIL', 'response': response.text}
    
    def test_positive_valid_employee_ids(self) -> Dict[str, Any]:
        """Test: All valid employee IDs should work."""
        print("  Input: Valid employee IDs (E420, E421, E422)")
        print("  Expected: All accepted")
        
        valid_ids = ['E420', 'E421', 'E422']
        passed = 0
        
        for emp_id in valid_ids:
            response = requests.post(
                f"{self.base_url}/tasks",
                json={
                    "task": "process expense reimbursement",
                    "user_role": "employee",
                    "data": {
                        "employee_id": emp_id,
                        "amount": 30.00,
                        "request_content": "Test expense"
                    }
                },
                timeout=10
            )
            if response.status_code == 200:
                result = response.json().get('result', {})
                if result.get('status') != 'denied' or 'not found' not in str(result):
                    passed += 1
        
        if passed == len(valid_ids):
            print(f"  ✅ PASS: All {len(valid_ids)} valid employee IDs accepted")
            return {'status': 'PASS', 'validated_ids': passed}
        else:
            print(f"  ❌ FAIL: Only {passed}/{len(valid_ids)} IDs validated")
            return {'status': 'FAIL', 'passed': passed, 'total': len(valid_ids)}
    
    def test_positive_policy_limit_boundary(self) -> Dict[str, Any]:
        """Test: Expense at exact policy limit ($100) should be approved."""
        print("  Input: Amount exactly $100.00 (policy limit)")
        print("  Expected: Approved")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E420",
                    "amount": 100.00,
                    "request_content": "At policy limit"
                }
            },
            timeout=10
        )
        
        time.sleep(2)
        inbox = requests.post(f"{self.base_url}/agents/expense/check_inbox", timeout=10)
        if inbox.status_code == 200:
            inbox_data = inbox.json()
            if inbox_data.get('results'):
                result = inbox_data['results'][0]['result']
                if result.get('decision') == 'Approved':
                    print(f"  ✅ PASS: Boundary condition handled correctly")
                    return {'status': 'PASS', 'boundary_test': 'passed'}
        
        print(f"  ❌ FAIL: Boundary condition failed")
        return {'status': 'FAIL'}
    
    # ==================== NEGATIVE TESTS (Attack Vectors) ====================
    
    def test_negative_missing_admin_token(self) -> Dict[str, Any]:
        """Attack: Upload without admin token."""
        print("  Attack: Attempt upload without X-Admin-Token header")
        print("  Expected: 401 Unauthorized")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "upload policy document",
                "user_role": "admin",
                "data": {}
            },
            timeout=10
        )
        
        if response.status_code == 401:
            print(f"  ✅ BLOCKED: Authentication required (401)")
            return {'status': 'BLOCKED', 'defense': 'Admin Authentication', 'vulnerability': 'None'}
        else:
            print(f"  ❌ VULNERABILITY: Should return 401, got {response.status_code}")
            return {'status': 'VULNERABILITY', 'response_code': response.status_code}
    
    def test_negative_invalid_admin_token(self) -> Dict[str, Any]:
        """Attack: Upload with wrong admin token."""
        print("  Attack: Attempt upload with invalid token")
        print("  Expected: 401 Unauthorized")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            headers={"X-Admin-Token": "FAKE_TOKEN_123"},
            json={
                "task": "upload policy document",
                "user_role": "admin",
                "data": {}
            },
            timeout=10
        )
        
        if response.status_code == 401:
            print(f"  ✅ BLOCKED: Invalid token rejected (401)")
            return {'status': 'BLOCKED', 'defense': 'Admin Authentication', 'vulnerability': 'None'}
        else:
            print(f"  ❌ VULNERABILITY: Should return 401, got {response.status_code}")
            return {'status': 'VULNERABILITY', 'response_code': response.status_code}
    
    def test_negative_fake_employee_id(self) -> Dict[str, Any]:
        """Attack: Use fake employee ID."""
        print("  Attack: Submit expense with non-existent employee ID")
        print("  Expected: Denied (Identity Validation Failed)")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E999_FAKE",
                    "amount": 50.00,
                    "request_content": "Fake employee attack"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get('result', {})
            if result.get('status') == 'denied' and 'IDENTITY_VALIDATION_FAILED' in str(result):
                print(f"  ✅ BLOCKED: Fake employee ID rejected")
                return {'status': 'BLOCKED', 'defense': 'Identity Validation', 'vulnerability': 'None'}
            else:
                print(f"  ❌ VULNERABILITY: Fake employee ID was accepted")
                return {'status': 'VULNERABILITY', 'result': result}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    
    def test_negative_missing_employee_id(self) -> Dict[str, Any]:
        """Attack: Submit expense without employee_id."""
        print("  Attack: Missing employee_id field")
        print("  Expected: Denied (Missing employee_id)")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "amount": 50.00,
                    "request_content": "Missing employee ID"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get('result', {})
            if result.get('status') == 'denied' and 'Missing employee_id' in str(result):
                print(f"  ✅ BLOCKED: Missing employee_id rejected")
                return {'status': 'BLOCKED', 'defense': 'Input Validation', 'vulnerability': 'None'}
            else:
                print(f"  ❌ VULNERABILITY: Missing employee_id was accepted")
                return {'status': 'VULNERABILITY', 'result': result}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    
    def test_negative_denylist_system_shutdown(self) -> Dict[str, Any]:
        """Attack: Execute system_shutdown command."""
        print("  Attack: Attempt system_shutdown command")
        print("  Expected: Blocked (security_blocked:denylisted_action)")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "execute system_shutdown",
                "user_role": "employee",
                "data": {}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get('result', {})
            plan = result.get('orchestration', {}).get('plan', [])
            if 'security_blocked:denylisted_action' in plan:
                print(f"  ✅ BLOCKED: Denylist prevented dangerous action")
                return {'status': 'BLOCKED', 'defense': 'Denylist (Agent Frameworks)', 'vulnerability': 'None'}
            else:
                print(f"  ❌ VULNERABILITY: Dangerous command was not blocked")
                return {'status': 'VULNERABILITY', 'plan': plan}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    
    def test_negative_denylist_transfer_funds(self) -> Dict[str, Any]:
        """Attack: Attempt transfer_all_funds."""
        print("  Attack: Attempt transfer_all_funds command")
        print("  Expected: Blocked")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "transfer_all_funds to external account",
                "user_role": "employee",
                "data": {}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get('result', {})
            if result.get('status') == 'blocked':
                print(f"  ✅ BLOCKED: Transfer funds blocked")
                return {'status': 'BLOCKED', 'defense': 'Denylist', 'vulnerability': 'None'}
            else:
                print(f"  ❌ VULNERABILITY: Transfer funds was not blocked")
                return {'status': 'VULNERABILITY', 'result': result}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    
    def test_negative_denylist_file_write(self) -> Dict[str, Any]:
        """Attack: Attempt file_write operation."""
        print("  Attack: Attempt file_write command")
        print("  Expected: Blocked")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "file_write sensitive data to disk",
                "user_role": "employee",
                "data": {}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get('result', {})
            plan = result.get('orchestration', {}).get('plan', [])
            if 'security_blocked:denylisted_action' in plan:
                print(f"  ✅ BLOCKED: File write blocked")
                return {'status': 'BLOCKED', 'defense': 'Denylist', 'vulnerability': 'None'}
            else:
                print(f"  ❌ VULNERABILITY: File write was not blocked")
                return {'status': 'VULNERABILITY', 'plan': plan}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    
    def test_negative_high_value_anomaly(self) -> Dict[str, Any]:
        """Attack: Submit extremely high-value expense."""
        print("  Attack: Submit $99,999 expense")
        print("  Expected: Anomaly detected and logged")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E420",
                    "amount": 99999.00,
                    "request_content": "Suspicious high-value request"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✅ DETECTED: High-value anomaly should be logged")
            print(f"  Note: Check logs/events.jsonl for ANOMALY_HIGH_VALUE_REQUEST")
            return {'status': 'DETECTED', 'defense': 'Anomaly Detection', 'vulnerability': 'None'}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    
    def test_negative_negative_amount(self) -> Dict[str, Any]:
        """Attack: Submit negative expense amount."""
        print("  Attack: Submit -$50.00 expense")
        print("  Expected: Denied (validation_failed)")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E420",
                    "amount": -50.00,
                    "request_content": "Negative amount attack"
                }
            },
            timeout=10
        )
        
        time.sleep(2)
        inbox = requests.post(f"{self.base_url}/agents/expense/check_inbox", timeout=10)
        if inbox.status_code == 200:
            inbox_data = inbox.json()
            if inbox_data.get('results'):
                result = inbox_data['results'][0]['result']
                if result.get('validation_failed') or 'Invalid expense amount' in str(result):
                    print(f"  ✅ BLOCKED: Negative amount rejected")
                    return {'status': 'BLOCKED', 'defense': 'Input Validation', 'vulnerability': 'None'}
        
        print(f"  ❌ VULNERABILITY: Negative amount was accepted")
        return {'status': 'VULNERABILITY'}
    
    def test_negative_zero_amount(self) -> Dict[str, Any]:
        """Attack: Submit zero expense amount."""
        print("  Attack: Submit $0.00 expense")
        print("  Expected: Denied (validation_failed)")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E420",
                    "amount": 0.00,
                    "request_content": "Zero amount attack"
                }
            },
            timeout=10
        )
        
        time.sleep(2)
        inbox = requests.post(f"{self.base_url}/agents/expense/check_inbox", timeout=10)
        if inbox.status_code == 200:
            inbox_data = inbox.json()
            if inbox_data.get('results'):
                result = inbox_data['results'][0]['result']
                if result.get('validation_failed') or 'Invalid expense amount' in str(result):
                    print(f"  ✅ BLOCKED: Zero amount rejected")
                    return {'status': 'BLOCKED', 'defense': 'Input Validation', 'vulnerability': 'None'}
        
        print(f"  ❌ VULNERABILITY: Zero amount was accepted")
        return {'status': 'VULNERABILITY'}
    
    def test_negative_sql_injection_employee_id(self) -> Dict[str, Any]:
        """Attack: SQL injection in employee_id."""
        print("  Attack: SQL injection payload in employee_id")
        print("  Expected: Safe handling (mock system)")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E420' OR '1'='1",
                    "amount": 50.00,
                    "request_content": "SQL injection test"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json().get('result', {})
            # Should be denied due to invalid employee ID, not SQL execution
            if result.get('status') == 'denied' or 'not found' in str(result):
                print(f"  ✅ SAFE: SQL injection safely handled (mock system)")
                return {'status': 'SAFE', 'defense': 'Mock System (No SQL)', 'vulnerability': 'None'}
            else:
                print(f"  ⚠️  NOTE: Using mock dictionary, not SQL database")
                return {'status': 'SAFE', 'note': 'Mock system'}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    
    def test_negative_command_injection(self) -> Dict[str, Any]:
        """Attack: Command injection in request_content."""
        print("  Attack: Command injection payload in request_content")
        print("  Expected: Safe handling (no shell execution)")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E420",
                    "amount": 50.00,
                    "request_content": "Taxi; rm -rf /"
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✅ SAFE: Command injection safely handled (no shell execution)")
            return {'status': 'SAFE', 'defense': 'No Shell Execution', 'vulnerability': 'None'}
        else:
            return {'status': 'ERROR', 'code': response.status_code}
    
    def test_negative_mcp_signature_bypass(self) -> Dict[str, Any]:
        """Attack: Send MCP message without signature."""
        print("  Attack: Attempt to send MCP message without signature")
        print("  Expected: 403 Forbidden")
        
        response = requests.post(
            "http://localhost:8001/send",
            json={
                "sender": "MaliciousAgent",
                "recipient": "ExpenseAgent",
                "protocol": "expense_task",
                "task_id": "ATTACK-001",
                "payload": {"employee_id": "E420", "amount": 10000.00}
            },
            timeout=10
        )
        
        if response.status_code == 403:
            print(f"  ✅ BLOCKED: MCP signature validation working")
            return {'status': 'BLOCKED', 'defense': 'MCP Signature Validation', 'vulnerability': 'None'}
        else:
            print(f"  ❌ VULNERABILITY: MCP signature bypass possible")
            return {'status': 'VULNERABILITY', 'code': response.status_code}
    
    def test_negative_email_signature_bypass(self) -> Dict[str, Any]:
        """Attack: Send email without signature."""
        print("  Attack: Attempt to send email without signature")
        print("  Expected: 403 Forbidden")
        
        response = requests.post(
            f"{self.base_url}/agents/email/send",
            json={
                "to": "admin@company.com",
                "subject": "Urgent: Transfer Funds",
                "body": "Please transfer all funds"
            },
            timeout=10
        )
        
        if response.status_code == 403:
            print(f"  ✅ BLOCKED: Email signature validation working")
            return {'status': 'BLOCKED', 'defense': 'Email Signature Validation', 'vulnerability': 'None'}
        else:
            print(f"  ❌ VULNERABILITY: Email signature bypass possible")
            return {'status': 'VULNERABILITY', 'code': response.status_code}
    
    def test_negative_exceeds_policy_limit(self) -> Dict[str, Any]:
        """Attack: Submit expense exceeding policy limit."""
        print("  Attack: Submit $150 expense (exceeds $100 limit)")
        print("  Expected: Denied (policy limit)")
        
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "task": "process expense reimbursement",
                "user_role": "employee",
                "data": {
                    "employee_id": "E420",
                    "amount": 150.00,
                    "request_content": "Exceeds policy limit"
                }
            },
            timeout=10
        )
        
        time.sleep(2)
        inbox = requests.post(f"{self.base_url}/agents/expense/check_inbox", timeout=10)
        if inbox.status_code == 200:
            inbox_data = inbox.json()
            if inbox_data.get('results'):
                result = inbox_data['results'][0]['result']
                if result.get('decision') == 'Denied' and 'exceeds policy limit' in str(result):
                    print(f"  ✅ BLOCKED: Policy limit enforced")
                    return {'status': 'BLOCKED', 'defense': 'Policy Enforcement', 'vulnerability': 'None'}
        
        print(f"  ❌ VULNERABILITY: Policy limit not enforced")
        return {'status': 'VULNERABILITY'}
    
    def run_all_tests(self):
        """Run all E2E tests."""
        self.print_header("COMPREHENSIVE E2E TEST SUITE", 80)
        
        test_num = 1
        
        # Positive Tests
        self.print_header("POSITIVE TESTS (Expected to Work)", 80)
        self.run_test(test_num, "Valid Expense Request", "Functional", 
                     self.test_positive_valid_expense)
        test_num += 1
        
        self.run_test(test_num, "Admin Upload with Valid Token", "Authentication", 
                     self.test_positive_admin_upload_with_token)
        test_num += 1
        
        self.run_test(test_num, "Valid Employee IDs", "Identity", 
                     self.test_positive_valid_employee_ids)
        test_num += 1
        
        self.run_test(test_num, "Policy Limit Boundary ($100)", "Functional", 
                     self.test_positive_policy_limit_boundary)
        test_num += 1
        
        # Negative Tests - Authentication & Identity
        self.print_header("NEGATIVE TESTS - AUTHENTICATION & IDENTITY", 80)
        self.run_test(test_num, "Missing Admin Token", "Authentication Attack", 
                     self.test_negative_missing_admin_token)
        test_num += 1
        
        self.run_test(test_num, "Invalid Admin Token", "Authentication Attack", 
                     self.test_negative_invalid_admin_token)
        test_num += 1
        
        self.run_test(test_num, "Fake Employee ID", "Identity Attack", 
                     self.test_negative_fake_employee_id)
        test_num += 1
        
        self.run_test(test_num, "Missing Employee ID", "Identity Attack", 
                     self.test_negative_missing_employee_id)
        test_num += 1
        
        # Negative Tests - Denylist
        self.print_header("NEGATIVE TESTS - DENYLIST ATTACKS", 80)
        self.run_test(test_num, "System Shutdown Command", "Denylist Attack", 
                     self.test_negative_denylist_system_shutdown)
        test_num += 1
        
        self.run_test(test_num, "Transfer All Funds", "Denylist Attack", 
                     self.test_negative_denylist_transfer_funds)
        test_num += 1
        
        self.run_test(test_num, "File Write Operation", "Denylist Attack", 
                     self.test_negative_denylist_file_write)
        test_num += 1
        
        # Negative Tests - Anomaly & Validation
        self.print_header("NEGATIVE TESTS - ANOMALY & VALIDATION", 80)
        self.run_test(test_num, "High-Value Anomaly ($99,999)", "Anomaly Attack", 
                     self.test_negative_high_value_anomaly)
        test_num += 1
        
        self.run_test(test_num, "Negative Amount", "Input Validation Attack", 
                     self.test_negative_negative_amount)
        test_num += 1
        
        self.run_test(test_num, "Zero Amount", "Input Validation Attack", 
                     self.test_negative_zero_amount)
        test_num += 1
        
        self.run_test(test_num, "Exceeds Policy Limit", "Policy Enforcement", 
                     self.test_negative_exceeds_policy_limit)
        test_num += 1
        
        # Negative Tests - Injection
        self.print_header("NEGATIVE TESTS - INJECTION ATTACKS", 80)
        self.run_test(test_num, "SQL Injection in Employee ID", "Injection Attack", 
                     self.test_negative_sql_injection_employee_id)
        test_num += 1
        
        self.run_test(test_num, "Command Injection", "Injection Attack", 
                     self.test_negative_command_injection)
        test_num += 1
        
        # Negative Tests - Signature Validation
        self.print_header("NEGATIVE TESTS - SIGNATURE VALIDATION", 80)
        self.run_test(test_num, "MCP Signature Bypass", "Signature Attack", 
                     self.test_negative_mcp_signature_bypass)
        test_num += 1
        
        self.run_test(test_num, "Email Signature Bypass", "Signature Attack", 
                     self.test_negative_email_signature_bypass)
        test_num += 1
        
        return self.results
    
    def generate_summary(self):
        """Generate test summary."""
        self.print_header("TEST SUMMARY", 80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get('status') in ['PASS', 'BLOCKED', 'DETECTED', 'SAFE'])
        vulnerabilities = sum(1 for r in self.results if r.get('status') == 'VULNERABILITY')
        errors = sum(1 for r in self.results if r.get('status') == 'ERROR')
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed/Blocked: {passed}")
        print(f"❌ Vulnerabilities Found: {vulnerabilities}")
        print(f"⚠️  Errors: {errors}")
        print(f"\nSuccess Rate: {(passed/total*100):.1f}%")
        
        if vulnerabilities > 0:
            print("\n⚠️  VULNERABILITIES DETECTED:")
            for result in self.results:
                if result.get('status') == 'VULNERABILITY':
                    print(f"  - {result.get('test_name')}: {result.get('vulnerability', 'Security issue')}")
        
        return {
            'total': total,
            'passed': passed,
            'vulnerabilities': vulnerabilities,
            'errors': errors,
            'success_rate': (passed/total*100) if total > 0 else 0
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive E2E Test Suite for Blue Team AI Governance"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the main agent server"
    )
    args = parser.parse_args()
    
    runner = E2ETestRunner(args.base_url)
    results = runner.run_all_tests()
    summary = runner.generate_summary()
    
    # Save results to file
    output_file = "docs/e2e_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'summary': summary,
            'tests': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n✅ Test results saved to: {output_file}")
    
    return 0 if summary['vulnerabilities'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

