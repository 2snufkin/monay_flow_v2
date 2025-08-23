"""
Input Validation and Sanitization Utilities

Provides comprehensive validation and sanitization functions for user inputs,
file paths, schema definitions, and data processing parameters.
"""

import re
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class InputValidator:
    """Comprehensive input validator for MoneyFlow application."""
    
    # Regular expressions for validation
    SCHEMA_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\s-]{1,100}$')
    COLLECTION_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
    COLUMN_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\s-]{1,255}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # File size limits
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_FILENAME_LENGTH = 255
    
    # Schema limits
    MAX_COLUMNS = 1000
    MAX_SCHEMA_NAME_LENGTH = 100
    MAX_COLLECTION_NAME_LENGTH = 64
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Validate file path for security and accessibility.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            path = Path(file_path)
            
            # Check if path exists
            if not path.exists():
                return False, f"File does not exist: {file_path}"
            
            # Check if it's a file (not directory)
            if not path.is_file():
                return False, f"Path is not a file: {file_path}"
            
            # Check file extension
            allowed_extensions = {'.xlsx', '.xls', '.xlsm'}
            if path.suffix.lower() not in allowed_extensions:
                return False, f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > InputValidator.MAX_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                max_mb = InputValidator.MAX_FILE_SIZE / (1024 * 1024)
                return False, f"File too large: {size_mb:.1f}MB (max: {max_mb}MB)"
            
            # Check filename length
            if len(path.name) > InputValidator.MAX_FILENAME_LENGTH:
                return False, f"Filename too long (max: {InputValidator.MAX_FILENAME_LENGTH} characters)"
            
            # Security check: prevent path traversal
            try:
                path.resolve().relative_to(Path.cwd().resolve())
            except ValueError:
                # Allow absolute paths but log them
                logger.warning(f"Using absolute path: {path}")
            
            return True, ""
            
        except Exception as e:
            return False, f"File validation error: {str(e)}"
    
    @staticmethod
    def validate_schema_name(name: str) -> Tuple[bool, str]:
        """
        Validate schema name.
        
        Args:
            name: Schema name to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not name or not isinstance(name, str):
            return False, "Schema name is required"
        
        name = name.strip()
        
        if len(name) == 0:
            return False, "Schema name cannot be empty"
        
        if len(name) > InputValidator.MAX_SCHEMA_NAME_LENGTH:
            return False, f"Schema name too long (max: {InputValidator.MAX_SCHEMA_NAME_LENGTH} characters)"
        
        if not InputValidator.SCHEMA_NAME_PATTERN.match(name):
            return False, "Schema name can only contain letters, numbers, spaces, hyphens, and underscores"
        
        # Check for reserved names
        reserved_names = {'admin', 'root', 'system', 'default', 'null', 'undefined'}
        if name.lower() in reserved_names:
            return False, f"'{name}' is a reserved name"
        
        return True, ""
    
    @staticmethod
    def validate_collection_name(name: str) -> Tuple[bool, str]:
        """
        Validate MongoDB collection name.
        
        Args:
            name: Collection name to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not name or not isinstance(name, str):
            return False, "Collection name is required"
        
        name = name.strip()
        
        if len(name) == 0:
            return False, "Collection name cannot be empty"
        
        if len(name) > InputValidator.MAX_COLLECTION_NAME_LENGTH:
            return False, f"Collection name too long (max: {InputValidator.MAX_COLLECTION_NAME_LENGTH} characters)"
        
        if not InputValidator.COLLECTION_NAME_PATTERN.match(name):
            return False, "Collection name can only contain letters, numbers, hyphens, and underscores"
        
        # MongoDB specific restrictions
        if name.startswith('system.'):
            return False, "Collection name cannot start with 'system.'"
        
        if '$' in name:
            return False, "Collection name cannot contain '$'"
        
        return True, ""
    
    @staticmethod
    def validate_column_names(column_names: List[str]) -> Tuple[bool, str]:
        """
        Validate list of column names.
        
        Args:
            column_names: List of column names to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(column_names, list):
            return False, "Column names must be a list"
        
        if len(column_names) == 0:
            return False, "At least one column name is required"
        
        if len(column_names) > InputValidator.MAX_COLUMNS:
            return False, f"Too many columns (max: {InputValidator.MAX_COLUMNS})"
        
        # Check for duplicates
        seen_names = set()
        normalized_names = []
        
        for i, name in enumerate(column_names):
            if not isinstance(name, str):
                return False, f"Column name at index {i} is not a string"
            
            name = name.strip()
            
            if len(name) == 0:
                return False, f"Column name at index {i} is empty"
            
            if len(name) > 255:
                return False, f"Column name at index {i} is too long (max: 255 characters)"
            
            # Normalize for duplicate check (case-insensitive)
            normalized = name.lower()
            if normalized in seen_names:
                return False, f"Duplicate column name: '{name}'"
            
            seen_names.add(normalized)
            normalized_names.append(name)
        
        return True, ""
    
    @staticmethod
    def validate_data_start_row(row: int) -> Tuple[bool, str]:
        """
        Validate data start row number.
        
        Args:
            row: Row number to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(row, int):
            return False, "Data start row must be an integer"
        
        if row < 1:
            return False, "Data start row must be at least 1"
        
        if row > 100:
            return False, "Data start row cannot exceed 100"
        
        return True, ""
    
    @staticmethod
    def validate_duplicate_strategy(strategy: str) -> Tuple[bool, str]:
        """
        Validate duplicate handling strategy.
        
        Args:
            strategy: Strategy to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(strategy, str):
            return False, "Duplicate strategy must be a string"
        
        valid_strategies = {'skip', 'update', 'upsert'}
        if strategy.lower() not in valid_strategies:
            return False, f"Invalid duplicate strategy. Must be one of: {', '.join(valid_strategies)}"
        
        return True, ""
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input by removing dangerous characters and trimming.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Remove control characters and normalize whitespace
        value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Remove potentially dangerous characters for file systems
        value = re.sub(r'[<>:"|?*\\]', '', value)
        
        # Truncate if necessary
        if max_length and len(value) > max_length:
            value = value[:max_length].strip()
        
        return value
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing dangerous characters.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            str: Sanitized filename
        """
        if not isinstance(filename, str):
            filename = str(filename)
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"|?*\\/]', '_', filename)
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1F\x7F]', '', filename)
        
        # Normalize whitespace
        filename = re.sub(r'\s+', '_', filename.strip())
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure it's not empty
        if not filename:
            filename = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Truncate if too long
        if len(filename) > InputValidator.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(filename)
            max_name_length = InputValidator.MAX_FILENAME_LENGTH - len(ext)
            filename = name[:max_name_length] + ext
        
        return filename
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(email, str):
            return False, "Email must be a string"
        
        email = email.strip().lower()
        
        if len(email) == 0:
            return False, "Email cannot be empty"
        
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email address too long"
        
        if not InputValidator.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_batch_size(batch_size: int) -> Tuple[bool, str]:
        """
        Validate batch size for processing.
        
        Args:
            batch_size: Batch size to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(batch_size, int):
            return False, "Batch size must be an integer"
        
        if batch_size < 1:
            return False, "Batch size must be at least 1"
        
        if batch_size > 10000:
            return False, "Batch size cannot exceed 10,000"
        
        return True, ""

def validate_schema_definition(schema_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate complete schema definition data.
    
    Args:
        schema_data: Schema definition dictionary
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate schema name
    if 'schema_name' in schema_data:
        is_valid, error = InputValidator.validate_schema_name(schema_data['schema_name'])
        if not is_valid:
            errors.append(f"Schema name: {error}")
    else:
        errors.append("Schema name is required")
    
    # Validate collection name
    if 'mongodb_collection_name' in schema_data:
        is_valid, error = InputValidator.validate_collection_name(schema_data['mongodb_collection_name'])
        if not is_valid:
            errors.append(f"Collection name: {error}")
    
    # Validate column names
    if 'excel_column_names' in schema_data:
        is_valid, error = InputValidator.validate_column_names(schema_data['excel_column_names'])
        if not is_valid:
            errors.append(f"Column names: {error}")
    else:
        errors.append("Column names are required")
    
    # Validate data start row
    if 'data_start_row' in schema_data:
        is_valid, error = InputValidator.validate_data_start_row(schema_data['data_start_row'])
        if not is_valid:
            errors.append(f"Data start row: {error}")
    
    # Validate duplicate strategy
    if 'duplicate_strategy' in schema_data:
        is_valid, error = InputValidator.validate_duplicate_strategy(schema_data['duplicate_strategy'])
        if not is_valid:
            errors.append(f"Duplicate strategy: {error}")
    
    return len(errors) == 0, errors

def sanitize_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize user input data dictionary.
    
    Args:
        data: Input data to sanitize
        
    Returns:
        Dict[str, Any]: Sanitized data
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = InputValidator.sanitize_string(value)
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            sanitized[key] = [InputValidator.sanitize_string(item) for item in value]
        else:
            sanitized[key] = value
    
    return sanitized
