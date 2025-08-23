"""
Data models for validation results.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ValidationResult:
    """
    Result of data validation operations.
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass
class MappingValidationResult:
    """
    Result of column mapping validation.
    """
    is_valid: bool
    mapped_columns: Dict[str, str]  # Excel name -> MongoDB name
    unmapped_excel_columns: List[str]
    missing_schema_columns: List[str]
    suggested_mappings: Dict[str, str]  # Fuzzy matches


@dataclass
class MappingResult:
    """
    Result of column mapping operation with issues.
    """
    normalized_data: dict
    issues: List[str]
    mapping_confidence: float



