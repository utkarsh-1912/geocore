# Author: Utkarsh Gupta
# License: GPL v3
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


class GeoAIUnitError(GeoAIValidationError):
    """Exception raised when parameter units have an incompatible dimension or invalid conversion."""
    def __init__(self, message: str, field: Optional[str] = None, provided_unit: Optional[str] = None, expected_unit: Optional[str] = None):
        errors = []
        if field:
            errors.append({
                "field": field,
                "message": message,
                "provided_unit": provided_unit,
                "expected_unit": expected_unit,
                "type": "unit_dimension_mismatch"
            })
        super().__init__(message, errors=errors)
        self.field = field
        self.provided_unit = provided_unit
        self.expected_unit = expected_unit
