"""
Column Mapping Module

Handles Excel to MongoDB field name translations and data type conversions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from fuzzywuzzy import fuzz

from src.models.schema_definition import SchemaDefinition, AttributeDefinition
from src.models.validation_result import MappingValidationResult, MappingResult


class ColumnMappingManager:
    """Manages column mapping between Excel and MongoDB fields."""
    
    def __init__(self):
        """Initialize ColumnMappingManager."""
        pass
    
    def find_excel_column_for_mongodb_field(self, mongodb_field: str, schema_def: SchemaDefinition) -> Optional[str]:
        """
        Reverse lookup: find Excel column name that maps to a MongoDB field.
        
        Args:
            mongodb_field: MongoDB field name (e.g., "customer_email")
            schema_def: Schema definition with mappings
            
        Returns:
            Excel column name (e.g., "Customer Email") or None if not found
        """
        for excel_col, attr_def in schema_def.normalized_attributes.items():
            if attr_def.field_name == mongodb_field:
                return excel_col
        return None
    
    def convert_value_to_type(self, value: Any, target_type: str) -> Any:
        """
        Convert Excel cell value to the target MongoDB data type.
        
        Args:
            value: Raw value from Excel cell
            target_type: Target type ("String", "Number", "Date", "Boolean")
            
        Returns:
            Converted value in correct type
            
        Raises:
            DataConversionError: If conversion fails
        """
        if pd.isna(value) or value is None:
            return None
        
        try:
            if target_type == "String":
                return str(value)
            elif target_type == "Number":
                return float(value) if '.' in str(value) else int(value)
            elif target_type == "Date":
                if isinstance(value, str):
                    return pd.to_datetime(value).to_pydatetime()
                return pd.to_datetime(value).to_pydatetime()
            elif target_type == "Boolean":
                if isinstance(value, str):
                    return value.lower() in ['true', '1', 'yes', 'y']
                return bool(value)
            else:
                return str(value)  # Default to string
                
        except Exception as e:
            raise ValueError(f"Failed to convert '{value}' to {target_type}: {str(e)}")
    
    def validate_column_mapping(self, excel_columns: List[str], schema_def: SchemaDefinition) -> MappingValidationResult:
        """
        Validate that Excel file columns can be properly mapped to schema.
        
        Args:
            excel_columns: Column names from Excel file
            schema_def: Schema definition to validate against
            
        Returns:
            Validation result with mapping success/issues
        """
        mapped_columns = {}
        unmapped_excel_columns = []
        missing_schema_columns = []
        suggested_mappings = {}
        
        schema_columns = list(schema_def.normalized_attributes.keys())
        
        # Check direct matches
        for excel_col in excel_columns:
            if excel_col in schema_columns:
                mapped_columns[excel_col] = schema_def.normalized_attributes[excel_col].field_name
            else:
                unmapped_excel_columns.append(excel_col)
        
        # Check for missing schema columns
        for schema_col in schema_columns:
            if schema_col not in excel_columns:
                missing_schema_columns.append(schema_col)
                
                # Try fuzzy matching
                best_match = self.find_closest_column_name(schema_col, excel_columns)
                if best_match and self.similarity_score(schema_col, best_match) > 0.8:
                    suggested_mappings[schema_col] = best_match
        
        is_valid = len(missing_schema_columns) == 0
        
        return MappingValidationResult(
            is_valid=is_valid,
            mapped_columns=mapped_columns,
            unmapped_excel_columns=unmapped_excel_columns,
            missing_schema_columns=missing_schema_columns,
            suggested_mappings=suggested_mappings
        )
    
    def handle_column_mapping_issues(self, raw_data: dict, schema_def: SchemaDefinition) -> MappingResult:
        """
        Handle various mapping edge cases like unmapped columns and fuzzy matching.
        
        Args:
            raw_data: Raw Excel row data
            schema_def: Schema definition with expected mappings
            
        Returns:
            Mapping result with normalized data and any issues found
        """
        normalized_data = {}
        issues = []
        mapping_confidence = 1.0
        
        # Process each expected schema column
        for excel_col, attr_def in schema_def.normalized_attributes.items():
            if excel_col in raw_data:
                try:
                    # Convert value to target type
                    converted_value = self.convert_value_to_type(raw_data[excel_col], attr_def.data_type)
                    normalized_data[attr_def.field_name] = converted_value
                except ValueError as e:
                    issues.append(f"Conversion error for {excel_col}: {str(e)}")
                    mapping_confidence *= 0.9
                    # Use original value as fallback
                    normalized_data[attr_def.field_name] = raw_data[excel_col]
            else:
                # Try fuzzy matching
                closest_match = self.find_closest_column_name(excel_col, list(raw_data.keys()))
                if closest_match and self.similarity_score(excel_col, closest_match) > 0.7:
                    issues.append(f"Using fuzzy match: '{excel_col}' -> '{closest_match}'")
                    mapping_confidence *= 0.8
                    try:
                        converted_value = self.convert_value_to_type(raw_data[closest_match], attr_def.data_type)
                        normalized_data[attr_def.field_name] = converted_value
                    except ValueError:
                        normalized_data[attr_def.field_name] = raw_data[closest_match]
                else:
                    issues.append(f"Missing column: {excel_col}")
                    mapping_confidence *= 0.7
                    normalized_data[attr_def.field_name] = None
        
        return MappingResult(
            normalized_data=normalized_data,
            issues=issues,
            mapping_confidence=mapping_confidence
        )
    
    def find_closest_column_name(self, target_column: str, available_columns: List[str]) -> Optional[str]:
        """
        Find the closest matching column name using fuzzy string matching.
        
        Args:
            target_column: Column name we're looking for
            available_columns: Available column names to match against
            
        Returns:
            Best matching column name or None if no good match
        """
        if not available_columns:
            return None
        
        best_match = None
        best_score = 0
        
        for available_col in available_columns:
            score = self.similarity_score(target_column, available_col)
            if score > best_score:
                best_score = score
                best_match = available_col
        
        return best_match if best_score > 0.6 else None
    
    def similarity_score(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score between two strings (0.0 to 1.0).
        
        Args:
            str1: First string to compare
            str2: Second string to compare
            
        Returns:
            Similarity score where 1.0 is exact match
        """
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings for comparison
        norm_str1 = str1.lower().replace(' ', '').replace('_', '').replace('-', '')
        norm_str2 = str2.lower().replace(' ', '').replace('_', '').replace('-', '')
        
        # Use fuzzy matching
        return fuzz.ratio(norm_str1, norm_str2) / 100.0
    
    def get_field_data_type(self, mongodb_field: str, schema_def: SchemaDefinition) -> str:
        """
        Get the expected data type for a MongoDB field from schema definition.
        
        Args:
            mongodb_field: MongoDB field name
            schema_def: Schema definition
            
        Returns:
            Data type string ("String", "Number", "Date", "Boolean")
        """
        for excel_col, attr_def in schema_def.normalized_attributes.items():
            if attr_def.field_name == mongodb_field:
                return attr_def.data_type
        return "String"  # Default fallback



