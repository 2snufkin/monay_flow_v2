"""
Data models for schema definitions and related classes.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class AttributeDefinition:
    """
    Definition of a single attribute/field mapping.
    """

    field_name: str  # MongoDB field name (normalized)
    data_type: str  # String, Number, Date, Boolean
    description: str
    is_required: bool = False


@dataclass
class IndexDefinition:
    """
    MongoDB index definition.
    """

    field_names: List[str]  # MongoDB field names for compound indexes
    index_type: str  # unique, ascending, descending, text
    reason: str


@dataclass
class CollectionDefinition:
    """
    Definition of a MongoDB collection within a schema.
    """

    name: str  # Collection name
    description: str  # Collection description
    created_at: datetime
    document_count: int = 0
    last_updated: Optional[datetime] = None


@dataclass
class SchemaDefinition:
    """
    Complete schema definition with column mappings and metadata.
    """

    schema_id: str
    schema_name: str
    database_name: str  # MongoDB database name (defaults to schema_name)
    excel_column_names: List[str]  # Original Excel column names
    normalized_attributes: Dict[
        str, AttributeDefinition
    ]  # Excel name -> MongoDB mapping
    suggested_indexes: List[IndexDefinition]
    duplicate_detection_columns: List[
        str
    ]  # MongoDB field names for duplicate detection
    duplicate_strategy: str  # 'skip', 'update', 'upsert'
    data_start_row: int  # Default data start row for this schema
    collections: List[CollectionDefinition]  # Array of collections in this schema
    created_at: datetime
    last_used: datetime
    usage_count: int
    # Legacy field for backward compatibility
    mongodb_collection_name: str = "excel_imports_default"


@dataclass
class AISchemaResponse:
    """
    Structured response from AI schema processing.
    """

    normalized_attributes: Dict[str, AttributeDefinition]
    suggested_indexes: List[IndexDefinition]
    duplicate_detection_columns: List[
        str
    ]  # List of column names for duplicate detection
    collection_name: str
