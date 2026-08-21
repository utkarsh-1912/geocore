"""
GeoAI Custom Exceptions
"""
from typing import List, Dict, Any, Optional

class GeoAIValidationError(Exception):
    """Exception raised when calculation input parameters fail validation."""
    def __init__(self, message: str, errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": "ValidationError",
            "error": self.message,
            "details": self.errors
        }
