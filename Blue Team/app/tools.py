from __future__ import annotations

from typing import Optional


class DriveAPI:
    """Mock Drive API for document management with RAG-supported search."""
    
    def __init__(self):
        """Initialize with mock file content dictionary."""
        self.store = {
            'policy_001.pdf': 'Max Reimbursement is $100.',
            'hr_policy_002.pdf': 'Standard Employee T&Cs.'
        }
    
    def search_file(self, query: str) -> str | None:
        """
        Search for files matching the query (RAG-supported search and retrieval).
        
        Args:
            query: Search query string
            
        Returns:
            File content if query matches file key, None otherwise
        """
        # Check if query is in any file key
        for filename, content in self.store.items():
            if query.lower() in filename.lower():
                return content
        return None
    
    def upload_file(self, filename: str, content: str) -> bool:
        """
        Upload a file to the store (Allows admin to upload).
        
        Args:
            filename: Name of the file to upload
            content: Content of the file
            
        Returns:
            True if upload successful
        """
        self.store[filename] = content
        return True


class HRSystemAPI:
    """Mock HR System API for employee financial management."""
    
    def __init__(self):
        """Initialize with mock employee database with financial information."""
        self.employees = {
            'E420': {
                'full_name': 'Alice Smith',
                'bank_account_id': '123456',
                'balance': 500.00
            },
            'E421': {
                'full_name': 'Bob Johnson',
                'bank_account_id': '789012',
                'balance': 750.00
            },
            'E422': {
                'full_name': 'Charlie Davis',
                'bank_account_id': '345678',
                'balance': 1000.00
            }
        }
    
    def get_profile(self, employee_id: str) -> dict | None:
        """
        Retrieve employee profile with financial information.
        
        Args:
            employee_id: Employee identifier
            
        Returns:
            Employee profile dictionary or None if not found
        """
        return self.employees.get(employee_id)
    
    def update_balance(self, employee_id: str, amount: float) -> bool:
        """
        Update employee reimbursement balance (simulates issuing reimbursements).
        
        Allows retrieval of employee financial information to "issue" reimbursements.
        
        Args:
            employee_id: Employee identifier
            amount: Amount to add to balance
            
        Returns:
            True if balance updated successfully, False otherwise
        """
        if employee_id not in self.employees:
            return False
        
        # Add the amount to the employee's balance
        self.employees[employee_id]['balance'] += amount
        return True

