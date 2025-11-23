"""
Red Team Test Suite - Advanced Security Validation

Tests sophisticated attack vectors against newly implemented security controls:
- Input validation bypass attempts
- Command whitelist evasion
- SQL injection payloads
- XSS attacks
- Command injection
- Second-order attacks
"""

import sys
import os
from pathlib import Path

# Add app directory to path for direct validator import
sys.path.insert(0, str(Path(__file__).parent / 'app'))

# Direct import of validators module to avoid app initialization
import validators
from validators import InputValidator, CommandWhitelistValidator, ValidationError, SanitizationContext


class RedTeamTestSuite:
    """
    Sophisticated Red Team attack simulations.
    
    Tests defense against:
    - SQL Injection (multiple variants)
    - Cross-Site Scripting (XSS)
    - Command Injection
    - Path Traversal
    - Second-Order Injection
    - Whitelist Bypass
    """
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.whitelist_validator = CommandWhitelistValidator()
        self.results = []
    
    def test_sql_injection_variant_1(self):
        """SQL Injection: Classic OR-based bypass"""
        payload = "E420' OR '1'='1"
        expected_outcome = "Input is rejected due to SQL injection pattern detection"
        
        try:
            self.input_validator.validate_employee_id(payload)
            result = "❌ VULNERABILITY: SQL injection payload was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'SQL Injection Variant 1 (OR-based)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_sql_injection_variant_2(self):
        """SQL Injection: UNION SELECT attack"""
        payload = "E420; DROP TABLE employees; --"
        expected_outcome = "Input is rejected due to SQL command detection"
        
        try:
            self.input_validator.validate_string_input(payload, "employee_note")
            result = "❌ VULNERABILITY: SQL DROP command was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'SQL Injection Variant 2 (DROP TABLE)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_sql_injection_variant_3(self):
        """SQL Injection: Stacked queries"""
        payload = "valid_input'; EXEC xp_cmdshell('rm -rf /'); --"
        expected_outcome = "Input is sanitized, stacked query fails"
        
        try:
            self.input_validator.validate_string_input(payload, "comment")
            result = "❌ VULNERABILITY: Stacked query was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'SQL Injection Variant 3 (Stacked Queries)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_xss_variant_1(self):
        """XSS: Script tag injection"""
        payload = "<script>alert(document.cookie)</script>"
        expected_outcome = "Script tags are detected and rejected"
        
        try:
            self.input_validator.validate_string_input(payload, "user_comment")
            result = "❌ VULNERABILITY: XSS payload was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'XSS Variant 1 (Script Tag)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_xss_variant_2(self):
        """XSS: Event handler injection"""
        payload = '<img src=x onerror="javascript:alert(\'XSS\')">'
        expected_outcome = "Event handler patterns are detected and rejected"
        
        try:
            self.input_validator.validate_string_input(payload, "profile_data")
            result = "❌ VULNERABILITY: Event handler XSS was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'XSS Variant 2 (Event Handler)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_xss_variant_3(self):
        """XSS: JavaScript protocol"""
        payload = '<a href="javascript:void(0)" onclick="steal_cookies()">Click</a>'
        expected_outcome = "JavaScript protocol is detected and rejected"
        
        try:
            self.input_validator.validate_string_input(payload, "link_description")
            result = "❌ VULNERABILITY: JavaScript protocol was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'XSS Variant 3 (JavaScript Protocol)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_command_injection_variant_1(self):
        """Command Injection: Shell metacharacter injection"""
        payload = "expense_report.pdf; rm -rf /"
        expected_outcome = "Shell metacharacters are detected and rejected"
        
        try:
            self.input_validator.validate_string_input(payload, "filename")
            result = "❌ VULNERABILITY: Command injection was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'Command Injection Variant 1 (Shell Metacharacter)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_command_injection_variant_2(self):
        """Command Injection: Command substitution"""
        payload = "data_$(cat /etc/passwd)"
        expected_outcome = "Command substitution syntax is detected and rejected"
        
        try:
            self.input_validator.validate_string_input(payload, "data_field")
            result = "❌ VULNERABILITY: Command substitution was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'Command Injection Variant 2 (Command Substitution)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_path_traversal(self):
        """Path Traversal: Directory traversal attack"""
        payload = "../../../etc/passwd"
        expected_outcome = "Path traversal patterns are detected and rejected"
        
        try:
            self.input_validator.validate_string_input(payload, "file_path")
            result = "❌ VULNERABILITY: Path traversal was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'Path Traversal Attack',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_whitelist_bypass_variant_1(self):
        """Whitelist Bypass: Dangerous command disguised"""
        payload = "system_shutdown --graceful"
        expected_outcome = "Dangerous command is detected in whitelist check and blocked"
        
        try:
            self.whitelist_validator.validate_and_log(payload, actor="red_team")
            result = "❌ VULNERABILITY: Dangerous command was NOT blocked by whitelist"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'Whitelist Bypass Variant 1 (Disguised Command)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_whitelist_bypass_variant_2(self):
        """Whitelist Bypass: Case variation attempt"""
        payload = "SYSTEM_SHUTDOWN"
        expected_outcome = "Case-insensitive matching detects dangerous command"
        
        try:
            self.whitelist_validator.validate_and_log(payload, actor="red_team")
            result = "❌ VULNERABILITY: Case variation bypass succeeded"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'Whitelist Bypass Variant 2 (Case Variation)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_whitelist_bypass_variant_3(self):
        """Whitelist Bypass: Command with obfuscation"""
        payload = "transfer_all_funds --to external_account"
        expected_outcome = "Substring matching detects dangerous operation substring"
        
        try:
            self.whitelist_validator.validate_and_log(payload, actor="red_team")
            result = "❌ VULNERABILITY: Obfuscated command was NOT blocked"
            status = "FAIL"
        except ValidationError as e:
            result = f"✅ BLOCKED: {str(e)}"
            status = "PASS"
        
        self.results.append({
            'test': 'Whitelist Bypass Variant 3 (Obfuscation)',
            'payload': payload,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def test_output_encoding(self):
        """Output Encoding: Verify HTML encoding prevents XSS"""
        malicious_input = "<script>alert('xss')</script>"
        expected_outcome = "Output is HTML-encoded, script does not execute"
        
        encoded = self.input_validator.sanitize_for_output(
            malicious_input,
            SanitizationContext.HTML
        )
        
        # Verify encoding happened
        if encoded == malicious_input:
            result = "❌ VULNERABILITY: HTML was NOT encoded"
            status = "FAIL"
        elif "&lt;script&gt;" in encoded or "&#x27;" in encoded:
            result = f"✅ SAFE: HTML encoded to: {encoded}"
            status = "PASS"
        else:
            result = "⚠️ PARTIAL: Encoding occurred but format unexpected"
            status = "PARTIAL"
        
        self.results.append({
            'test': 'Output Encoding (HTML Context)',
            'payload': malicious_input,
            'expected': expected_outcome,
            'result': result,
            'status': status
        })
        return status == "PASS"
    
    def run_all_tests(self):
        """Execute all Red Team tests and generate report."""
        print("\n" + "="*80)
        print("RED TEAM SECURITY VALIDATION - Advanced Attack Simulations".center(80))
        print("=" * 80 + "\n")
        
        # Run all tests
        tests = [
            self.test_sql_injection_variant_1,
            self.test_sql_injection_variant_2,
            self.test_sql_injection_variant_3,
            self.test_xss_variant_1,
            self.test_xss_variant_2,
            self.test_xss_variant_3,
            self.test_command_injection_variant_1,
            self.test_command_injection_variant_2,
            self.test_path_traversal,
            self.test_whitelist_bypass_variant_1,
            self.test_whitelist_bypass_variant_2,
            self.test_whitelist_bypass_variant_3,
            self.test_output_encoding
        ]
        
        for test in tests:
            test()
        
        # Generate summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        
        print(f"\n{'TEST RESULTS':^80}\n")
        print("-" * 80)
        for result in self.results:
            status_symbol = "✅" if result['status'] == "PASS" else "❌"
            print(f"{status_symbol} {result['test']}")
            print(f"   Payload: {result['payload'][:60]}...")
            print(f"   Expected: {result['expected']}")
            print(f"   Result: {result['result']}")
            print("-" * 80)
        
        print(f"\nSUMMARY:")
        print(f"  Total Tests: {total}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  Success Rate: {(passed/total*100):.1f}%\n")
        
        if failed == 0:
            print("="*80)
            print("✅ ALL RED TEAM TESTS PASSED - Security controls verified".center(80))
            print("="*80)
            return 0
        else:
            print("="*80)
            print(f"⚠️ {failed} VULNERABILITIES DETECTED - Review required".center(80))
            print("="*80)
            return 1


if __name__ == "__main__":
    suite = RedTeamTestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)
