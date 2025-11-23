from __future__ import annotations

import logging

from .tools import DriveAPI, HRSystemAPI
from .validators import InputValidator, ValidationError


logger = logging.getLogger(__name__)


class ExpenseAgent:
    """
    Specialized Agent for Expense Management workflow.
    
    Implements:
    - Policy retrieval via Drive API
    - Report review and decision logic
    - Reimbursement processing via HR System API
    """
    
    def __init__(self, drive_api: DriveAPI, hr_api: HRSystemAPI):
        """
        Initialize the Expense Agent with API dependencies.
        
        Args:
            drive_api: DriveAPI instance for document management
            hr_api: HRSystemAPI instance for employee management
        """
        self.drive_api = drive_api
        self.hr_api = hr_api
        logger.info("ExpenseAgent initialized with DriveAPI and HRSystemAPI")
    
    def process_report(
        self, 
        employee_id: str, 
        expense_amount: float, 
        request_content: str
    ) -> dict:
        """
        Process an expense report through the full Expense management workflow.
        
        Workflow:
        1. Policy Retrieval: Use Drive API to retrieve expense policy
        2. Report Review/Decision: Determine approval based on policy
        3. Reimbursement (If Approved): Update employee balance via HR API
        
        Args:
            employee_id: Employee identifier (e.g., 'E420')
            expense_amount: Amount of expense to reimburse
            request_content: Description of the expense request
            
        Returns:
            Dictionary containing:
            - decision: 'Approved' or 'Denied'
            - policy_context: Policy used for decision
            - reimbursement_amount: Amount reimbursed (0 if denied)
            - new_balance: Employee's new balance (if approved)
        """
        # ⚠️ SECURITY-CRITICAL: Input Validation
        # MANDATORY: All inputs validated before processing
        # Prevents SQL injection, XSS, command injection
        
        validator = InputValidator()
        
        # Step 0: Input Validation with comprehensive checks
        try:
            # Validate employee ID format
            employee_id = validator.validate_employee_id(employee_id)
            
            # Validate expense amount
            expense_amount = validator.validate_amount(expense_amount)
            
            # Sanitize request content (prevent XSS/injection)
            request_content = validator.validate_string_input(
                request_content,
                field_name="request_content",
                max_length=500,
                allow_html=False
            )
            
            logger.info(
                f"[ExpenseAgent] Input validation passed for {employee_id}, "
                f"amount: ${expense_amount}"
            )
            
        except ValidationError as e:
            logger.error(f"[ExpenseAgent] Input validation failed: {e}")
            return {
                'decision': 'Denied',
                'policy_context': 'Input validation policy',
                'reimbursement_amount': 0.0,
                'error': str(e),
                'validation_failed': True,
                'security_check': 'INPUT_VALIDATION_FAILED'
            }
        
        # Step 1: Policy Retrieval - Use Drive API to get expense policy
        logger.info(f"[ExpenseAgent] Retrieving policy for expense report: {employee_id}")
        policy_content = self.drive_api.search_file('policy')
        
        if not policy_content:
            logger.warning("[ExpenseAgent] Policy not found, using default")
            policy_content = "Max Reimbursement is $100."
        
        logger.info(f"[ExpenseAgent] Policy retrieved: {policy_content}")
        
        # Step 2: Report Review/Decision
        # Based on mock policy: expense_amount <= 100.00 is approved
        if expense_amount <= 100.00:
            decision = 'Approved'
            logger.info(f"[ExpenseAgent] Expense APPROVED for {employee_id}: ${expense_amount}")
            
            # Step 3: Reimbursement (If Approved)
            # 3a: Validate employee exists
            employee_profile = self.hr_api.get_profile(employee_id)
            
            if not employee_profile:
                logger.error(f"[ExpenseAgent] Employee {employee_id} not found")
                return {
                    'decision': 'Denied',
                    'policy_context': policy_content,
                    'reimbursement_amount': 0.0,
                    'error': f'Employee {employee_id} not found in HR system'
                }
            
            # 3b: Update balance (issue reimbursement)
            update_success = self.hr_api.update_balance(employee_id, expense_amount)
            
            if not update_success:
                logger.error(f"[ExpenseAgent] Failed to update balance for {employee_id}")
                return {
                    'decision': 'Denied',
                    'policy_context': policy_content,
                    'reimbursement_amount': 0.0,
                    'error': 'Failed to update employee balance'
                }
            
            # 3c: Get new balance
            updated_profile = self.hr_api.get_profile(employee_id)
            new_balance = updated_profile['balance'] if updated_profile else 0.0
            
            logger.info(f"[ExpenseAgent] Balance updated. New balance: ${new_balance}")
            
            return {
                'decision': decision,
                'policy_context': policy_content,
                'reimbursement_amount': expense_amount,
                'new_balance': new_balance,
                'employee_name': employee_profile['full_name']
            }
            
        else:
            # Denied - expense exceeds policy limit
            decision = 'Denied'
            logger.info(f"[ExpenseAgent] Expense DENIED for {employee_id}: ${expense_amount} exceeds limit")
            
            return {
                'decision': decision,
                'policy_context': policy_content,
                'reimbursement_amount': 0.0,
                'reason': f'Expense amount ${expense_amount} exceeds policy limit ($100.00)'
            }

