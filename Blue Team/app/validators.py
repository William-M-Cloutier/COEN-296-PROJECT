"""
Input Validation and Sanitization Framework

Provides comprehensive input validation, output encoding, and injection prevention
for the Blue Team AI Governance project.
"""

import re
import html
import json
from typing import Any, Dict, Optional, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class SanitizationContext(Enum):
    """Context for output encoding."""
    HTML = "html"
    JSON = "json"
    SQL = "sql"
    SHELL = "shell"
    LOG = "log"


class InputValidator:
    """
    Comprehensive input validation to prevent injection attacks.
    
    Implements defense against:
    - SQL Injection
    - Command Injection
    - XSS (Cross-Site Scripting)
    - Path Traversal
    - Second-Order Injection
    """
    
    # Dangerous patterns that indicate potential attacks
    SQL_INJECTION_PATTERNS = [
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(--|#|\/\*|\*\/)",
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(';|\"|`)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"\$\(",
        r"\.\./",
        r"/etc/",
        r"/root/",
        r"rm\s+-",
        r"shutdown",
        r"reboot",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\./\.\./",
        r"\.\.\\",
        r"/etc/",
        r"/root/",
        r"C:\\Windows",
    ]
    
    @staticmethod
    def validate_employee_id(employee_id: str) -> str:
        """
        Validate employee ID format.
        
        Args:
            employee_id: Employee identifier
            
        Returns:
            Validated employee ID
            
        Raises:
            ValidationError: If format is invalid
        """
        if not employee_id:
            raise ValidationError("Employee ID cannot be empty")
        
        # Expected format: E followed by 3 digits (e.g., E420)
        pattern = r"^E[0-9]{3}$"
        if not re.match(pattern, employee_id):
            logger.warning(f"[Validation] Invalid employee ID format: {employee_id}")
            raise ValidationError(
                f"Invalid employee ID format. Expected format: E### (e.g., E420)"
            )
        
        return employee_id
    
    @staticmethod
    def validate_amount(amount: Union[float, int, str]) -> float:
        """
        Validate monetary amount.
        
        Args:
            amount: Monetary amount
            
        Returns:
            Validated amount as float
            
        Raises:
            ValidationError: If amount is invalid
        """
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid amount format: {amount}")
        
        if amount_float <= 0:
            raise ValidationError("Amount must be greater than zero")
        
        if amount_float > 1000000:  # $1M limit
            raise ValidationError("Amount exceeds maximum allowed value")
        
        # Round to 2 decimal places
        return round(amount_float, 2)
    
    @staticmethod
    def validate_string_input(
        value: str,
        field_name: str,
        max_length: int = 1000,
        allow_html: bool = False
    ) -> str:
        """
        Validate and sanitize string input.
        
        Args:
            value: Input string
            field_name: Name of the field (for error messages)
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML tags
            
        Returns:
            Sanitized string
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} exceeds maximum length of {max_length} characters"
            )
        
        # Check for SQL injection patterns
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(
                    f"[Security] Potential SQL injection in {field_name}: {value[:50]}"
                )
                raise ValidationError(f"{field_name} contains prohibited SQL patterns")
        
        # Check for command injection patterns
        for pattern in InputValidator.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value):
                logger.warning(
                    f"[Security] Potential command injection in {field_name}: {value[:50]}"
                )
                raise ValidationError(
                    f"{field_name} contains prohibited shell characters"
                )
        
        # Check for XSS patterns (unless HTML is explicitly allowed)
        if not allow_html:
            for pattern in InputValidator.XSS_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    logger.warning(
                        f"[Security] Potential XSS in {field_name}: {value[:50]}"
                    )
                    raise ValidationError(f"{field_name} contains prohibited HTML/script content")
        
        # Check for path traversal
        for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value):
                logger.warning(
                    f"[Security] Potential path traversal in {field_name}: {value[:50]}"
                )
                raise ValidationError(f"{field_name} contains prohibited path patterns")
        
        return value.strip()
    
    @staticmethod
    def sanitize_for_output(value: Any, context: SanitizationContext) -> str:
        """
        Sanitize value for safe output in different contexts.
        
        Args:
            value: Value to sanitize
            context: Output context (HTML, JSON, SQL, etc.)
            
        Returns:
            Sanitized string safe for the specified context
        """
        if value is None:
            return ""
        
        value_str = str(value)
        
        if context == SanitizationContext.HTML:
            # HTML entity encoding
            return html.escape(value_str, quote=True)
        
        elif context == SanitizationContext.JSON:
            # JSON encoding
            return json.dumps(value_str)
        
        elif context == SanitizationContext.LOG:
            # Remove control characters and limit length
            sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value_str)
            return sanitized[:500]  # Limit log length
        
        elif context == SanitizationContext.SHELL:
            # Shell escaping - remove all special characters
            return re.sub(r'[^a-zA-Z0-9_\- ]', '', value_str)
        
        else:
            return value_str


class CommandWhitelistValidator:
    """
    Validates commands against whitelist to prevent dangerous operations.
    Implements the Anti-Destruction Layer.
    """
    
    def __init__(self, whitelist_path: str = "agent_whitelist.json"):
        """
        Initialize with whitelist configuration.
        
        Args:
            whitelist_path: Path to whitelist JSON file
        """
        import json
        from pathlib import Path
        
        self.whitelist_path = Path(whitelist_path)
        self.config = self._load_whitelist()
    
    def _load_whitelist(self) -> Dict:
        """Load whitelist configuration from JSON file."""
        try:
            with open(self.whitelist_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Whitelist file not found: {self.whitelist_path}")
            # Fail closed - no commands allowed if whitelist missing
            return {
                "allowed_commands": {},
                "blocked_commands": {"all": ["*"]},
                "security_policy": {"strict_mode": True, "fail_closed": True}
            }
    
    def is_command_allowed(self, command: str) -> tuple[bool, Optional[str]]:
        """
        Check if command is allowed by whitelist.
        
        Args:
            command: Command to validate
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        command_lower = command.lower().strip()
        
        # Check for prohibited patterns first
        prohibited_patterns = self.config.get("validation_rules", {}).get(
            "command_format", {}
        ).get("prohibited_patterns", [])
        
        for pattern in prohibited_patterns:
            if pattern in command_lower:
                logger.warning(
                    f"[CommandWhitelist] Blocked prohibited pattern: {pattern} in {command[:50]}"
                )
                return False, f"Contains prohibited pattern: {pattern}"
        
        # Check blocked commands
        blocked = self.config.get("blocked_commands", {})
        for category, commands in blocked.items():
            for blocked_cmd in commands:
                if blocked_cmd.lower() in command_lower:
                    logger.error(
                        f"[CommandWhitelist] BLOCKED HIGH-RISK COMMAND: {command[:50]}"
                    )
                    return False, f"Blocked by {category}: {blocked_cmd}"
        
        # Check allowed commands (for strict mode)
        if self.config.get("security_policy", {}).get("strict_mode", False):
            allowed = self.config.get("allowed_commands", {})
            is_allowed = False
            
            for category, commands in allowed.items():
                for allowed_cmd in commands:
                    if allowed_cmd.lower() in command_lower:
                        is_allowed = True
                        break
                if is_allowed:
                    break
            
            if not is_allowed:
                logger.warning(
                    f"[CommandWhitelist] Command not in whitelist: {command[:50]}"
                )
                return False, "Command not in approved whitelist"
        
        # Command is allowed
        return True, None
    
    def validate_and_log(self, command: str, actor: str = "unknown") -> bool:
        """
        Validate command and log result.
        
        Args:
            command: Command to validate
            actor: Who is executing the command
            
        Returns:
            True if command is allowed, False otherwise
            
        Raises:
            ValidationError: If command is blocked
        """
        is_allowed, reason = self.is_command_allowed(command)
        
        log_entry = {
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            "actor": actor,
            "action": "command_validation",
            "command": command,
            "result": "ALLOWED" if is_allowed else "BLOCKED",
            "reason": reason
        }
        
        if not is_allowed:
            log_entry["severity"] = "HIGH"
            log_entry["alert"] = "BLOCKED_HIGH_RISK_COMMAND"
            logger.error(f"[Security Alert] {log_entry}")
            
            # Write to security event log
            self._log_security_event(log_entry)
            
            raise ValidationError(
                f"Command blocked by security policy: {reason}"
            )
        
        logger.info(f"[CommandWhitelist] Command allowed: {command[:50]}")
        return True
    
    def _log_security_event(self, event: Dict) -> None:
        """Log security event to events.jsonl."""
        from pathlib import Path
        import json
        
        log_dir = Path("./logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        events_log = log_dir / "events.jsonl"
        
        with events_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")


# Example usage and test cases
if __name__ == "__main__":
    # Test input validation
    validator = InputValidator()
    
    # Test employee ID validation
    try:
        valid_id = validator.validate_employee_id("E420")
        print(f"✅ Valid employee ID: {valid_id}")
    except ValidationError as e:
        print(f"❌ {e}")
    
    # Test SQL injection prevention
    try:
        validator.validate_string_input("John'; DROP TABLE users;--", "username")
        print("❌ SQL injection was not blocked!")
    except ValidationError as e:
        print(f"✅ SQL injection blocked: {e}")
    
    # Test XSS prevention
    try:
        validator.validate_string_input("<script>alert('xss')</script>", "comment")
        print("❌ XSS was not blocked!")
    except ValidationError as e:
        print(f"✅ XSS blocked: {e}")
    
    # Test command whitelist
    whitelist_validator = CommandWhitelistValidator()
    
    try:
        whitelist_validator.validate_and_log("status", actor="test_agent")
        print("✅ Safe command allowed")
    except ValidationError as e:
        print(f"❌ Safe command blocked: {e}")
    
    try:
        whitelist_validator.validate_and_log("system_shutdown", actor="malicious_agent")
        print("❌ Dangerous command was not blocked!")
    except ValidationError as e:
        print(f"✅ Dangerous command blocked: {e}")
