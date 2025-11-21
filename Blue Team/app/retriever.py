from __future__ import annotations

from datetime import datetime
from typing import Optional


class Retriever:
    """
    Retriever with provenance tracking for Data Operations.
    
    Simulates vector DB with provenance metadata:
    - Tracks source_id for each document
    - Records timestamp of ingestion
    - Flags sanitization status
    """
    
    def __init__(self):
        """Initialize retriever with mock documents and provenance data."""
        # Mock document store mapping content to provenance attributes
        self.store = {
            'Expense policy: claims under $100 auto-approve.': {
                'source_id': 'DOC-123',
                'timestamp': '2024-01-15T10:30:00Z',
                'sanitized': True
            },
            'Travel policy: Business class flights require VP approval.': {
                'source_id': 'DOC-124',
                'timestamp': '2024-01-20T14:15:00Z',
                'sanitized': True
            },
            'Confidential: Employee salary ranges by department.': {
                'source_id': 'DOC-125',
                'timestamp': '2024-02-01T09:00:00Z',
                'sanitized': False
            },
            'HR policy: Standard employee terms and conditions.': {
                'source_id': 'DOC-126',
                'timestamp': '2024-01-10T08:00:00Z',
                'sanitized': True
            }
        }
    
    def get_context(self, key: str) -> dict:
        """
        Retrieve document with provenance metadata.
        
        Simulates sanitization based on key:
        - 'policy' returns sanitized content
        - 'confidential' returns unsanitized content
        
        Args:
            key: Search key for document retrieval
            
        Returns:
            Dictionary with document content and provenance data:
            - content: Document text
            - source_id: Source document identifier
            - timestamp: Ingestion timestamp
            - sanitized: Whether content was sanitized
        """
        key_lower = key.lower()
        
        # Search for matching documents
        for content, provenance in self.store.items():
            content_lower = content.lower()
            
            # Handle 'policy' key - return sanitized policy
            if key_lower == 'policy' and 'policy' in content_lower and 'confidential' not in content_lower:
                return {
                    'content': content,
                    'source_id': provenance['source_id'],
                    'timestamp': provenance['timestamp'],
                    'sanitized': True
                }
            
            # Handle 'confidential' key - return unsanitized confidential data
            elif key_lower == 'confidential' and 'confidential' in content_lower:
                return {
                    'content': content,
                    'source_id': provenance['source_id'],
                    'timestamp': provenance['timestamp'],
                    'sanitized': False
                }
            
            # General search by key in content
            elif key_lower in content_lower:
                return {
                    'content': content,
                    'source_id': provenance['source_id'],
                    'timestamp': provenance['timestamp'],
                    'sanitized': provenance['sanitized']
                }
        
        # No match found
        return {
            'content': None,
            'source_id': None,
            'timestamp': datetime.now().isoformat(),
            'sanitized': False,
            'error': f'No document found for key: {key}'
        }


def get_kb() -> KnowledgeBaseManager:
    """Return a KnowledgeBaseManager using current settings with provenance tracking."""
    settings = get_settings()
    provenance = ProvenanceTracker(settings.data)
    return KnowledgeBaseManager(settings.data, provenance)


