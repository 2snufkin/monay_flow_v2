"""
Schema Management Module

Handles CRUD operations for schema definitions in SQLite database.
"""

import uuid
import json
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional

from models.schema_definition import SchemaDefinition, AttributeDefinition, IndexDefinition
from config.database_config import get_sqlite_connection

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages schema definitions in SQLite database."""
    
    def __init__(self):
        """Initialize SchemaManager."""
        pass
    
    def get_all_schemas(self) -> List[SchemaDefinition]:
        """
        Retrieve all schema definitions from SQL database.
        
        Returns:
            List of all available schema definitions ordered by last_used DESC
        """
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT schema_id, schema_name, original_columns, normalized_attributes,
                   suggested_indexes, duplicate_detection_columns, duplicate_strategy,
                   data_start_row, mongodb_collection_name, created_at, last_used, usage_count
            FROM schema_definitions 
            ORDER BY last_used DESC
        """)
        
        rows = cursor.fetchall()
        schemas = []
        
        for row in rows:
            # Deserialize normalized attributes
            normalized_attrs = {}
            if row['normalized_attributes']:
                try:
                    attrs_data = json.loads(row['normalized_attributes'])
                    for key, value in attrs_data.items():
                        if isinstance(value, dict):
                            normalized_attrs[key] = AttributeDefinition(**value)
                        else:
                            normalized_attrs[key] = value
                except Exception as e:
                    logger.warning(f"Failed to deserialize normalized_attributes: {e}")
            
            # Deserialize suggested indexes
            suggested_indexes = []
            if row['suggested_indexes']:
                try:
                    indexes_data = json.loads(row['suggested_indexes'])
                    for idx_data in indexes_data:
                        if isinstance(idx_data, dict):
                            suggested_indexes.append(IndexDefinition(**idx_data))
                        else:
                            suggested_indexes.append(idx_data)
                except Exception as e:
                    logger.warning(f"Failed to deserialize suggested_indexes: {e}")
            
            schema = SchemaDefinition(
                schema_id=row['schema_id'],
                schema_name=row['schema_name'],
                excel_column_names=json.loads(row['original_columns']) if row['original_columns'] else [],
                normalized_attributes=normalized_attrs,
                suggested_indexes=suggested_indexes,
                duplicate_detection_columns=json.loads(row['duplicate_detection_columns']) if row['duplicate_detection_columns'] else [],
                duplicate_strategy=row['duplicate_strategy'],
                data_start_row=row['data_start_row'],
                mongodb_collection_name=row['mongodb_collection_name'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                last_used=datetime.fromisoformat(row['last_used']) if row['last_used'] else datetime.now(),
                usage_count=row['usage_count']
            )
            schemas.append(schema)
        
        return schemas
    
    def create_schema(self, schema_name: str, column_names: List[str]) -> str:
        """
        Generate unique schema_id and initiate AI processing workflow.
        
        Args:
            schema_name: User-provided name for the schema
            column_names: List of column names pasted from Excel
            
        Returns:
            Generated schema_id for tracking the creation process
        """
        schema_id = f"schema_{uuid.uuid4().hex[:8]}"
        return schema_id
    
    def save_schema_definition(self, schema_data: SchemaDefinition) -> bool:
        """
        Save AI-processed schema definition to SQL database.
        
        Args:
            schema_data: Complete schema definition with AI suggestions
            
        Returns:
            True if saved successfully, False otherwise
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Attempting to save schema: {schema_data.schema_name}")
        logger.debug(f"Schema ID: {schema_data.schema_id}, Columns: {len(schema_data.excel_column_names)}, Collection: {schema_data.mongodb_collection_name}")
        
        try:
            logger.debug("Getting database connection...")
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            logger.debug("Database connection established")
            
            logger.debug("Executing INSERT statement...")
            # Ensure datetime fields are valid datetime objects
            if not schema_data.created_at or not isinstance(schema_data.created_at, datetime):
                schema_data.created_at = datetime.now()
            if not schema_data.last_used or not isinstance(schema_data.last_used, datetime):
                schema_data.last_used = datetime.now()
            
            cursor.execute("""
                INSERT INTO schema_definitions 
                (schema_id, schema_name, original_columns, normalized_attributes,
                 suggested_indexes, duplicate_detection_columns, duplicate_strategy,
                 data_start_row, mongodb_collection_name, created_at, last_used, usage_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                schema_data.schema_id,
                schema_data.schema_name,
                json.dumps(schema_data.excel_column_names),
                json.dumps({k: v.__dict__ if hasattr(v, '__dict__') else v for k, v in schema_data.normalized_attributes.items()}),
                json.dumps([idx.__dict__ if hasattr(idx, '__dict__') else idx for idx in schema_data.suggested_indexes]),
                json.dumps(schema_data.duplicate_detection_columns),
                schema_data.duplicate_strategy,
                schema_data.data_start_row,
                schema_data.mongodb_collection_name,
                schema_data.created_at.isoformat(),
                schema_data.last_used.isoformat(),
                schema_data.usage_count
            ))
            
            logger.debug("Committing transaction...")
            conn.commit()
            logger.debug("Transaction committed successfully")
            
            logger.info(f"Schema '{schema_data.schema_name}' saved successfully!")
            return True
            
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error saving schema: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving schema definition: {e}")
            logger.debug("Stack trace:", exc_info=True)
            return False
    
    def get_schema_by_id(self, schema_id: str) -> Optional[SchemaDefinition]:
        """
        Retrieve specific schema definition by ID.
        
        Args:
            schema_id: Unique identifier for the schema
            
        Returns:
            Schema definition if found, None otherwise
        """
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT schema_id, schema_name, original_columns, normalized_attributes,
                   suggested_indexes, duplicate_detection_columns, duplicate_strategy,
                   data_start_row, mongodb_collection_name, created_at, last_used, usage_count
            FROM schema_definitions 
            WHERE schema_id = ?
        """, (schema_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Deserialize normalized attributes
        normalized_attrs = {}
        if row['normalized_attributes']:
            try:
                attrs_data = json.loads(row['normalized_attributes'])
                for key, value in attrs_data.items():
                    if isinstance(value, dict):
                        normalized_attrs[key] = AttributeDefinition(**value)
                    else:
                        normalized_attrs[key] = value
            except Exception as e:
                logger.warning(f"Failed to deserialize normalized_attributes: {e}")
        
        # Deserialize suggested indexes
        suggested_indexes = []
        if row['suggested_indexes']:
            try:
                indexes_data = json.loads(row['suggested_indexes'])
                for idx_data in indexes_data:
                    if isinstance(idx_data, dict):
                        suggested_indexes.append(IndexDefinition(**idx_data))
                    else:
                        suggested_indexes.append(idx_data)
            except Exception as e:
                logger.warning(f"Failed to deserialize suggested_indexes: {e}")
        
        return SchemaDefinition(
            schema_id=row['schema_id'],
            schema_name=row['schema_name'],
            excel_column_names=json.loads(row['original_columns']) if row['original_columns'] else [],
            normalized_attributes=normalized_attrs,
            suggested_indexes=suggested_indexes,
            duplicate_detection_columns=json.loads(row['duplicate_detection_columns']) if row['duplicate_detection_columns'] else [],
            duplicate_strategy=row['duplicate_strategy'],
            data_start_row=row['data_start_row'],
            mongodb_collection_name=row['mongodb_collection_name'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
            last_used=datetime.fromisoformat(row['last_used']) if row['last_used'] else datetime.now(),
            usage_count=row['usage_count']
        )
    
    def update_schema_usage(self, schema_id: str) -> None:
        """
        Increment usage count and update last_used timestamp.
        
        Args:
            schema_id: Schema that was used for import
        """
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE schema_definitions 
            SET usage_count = usage_count + 1,
                last_used = ?
            WHERE schema_id = ?
        """, (datetime.now().isoformat(), schema_id))
        
        conn.commit()
    
    def update_schema_data_start_row(self, schema_id: str, start_row: int) -> bool:
        """
        Update the default data start row for a schema.
        
        Args:
            schema_id: Schema to update
            start_row: New default start row (1-10)
            
        Returns:
            True if updated successfully
        """
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE schema_definitions 
                SET data_start_row = ?
                WHERE schema_id = ?
            """, (start_row, schema_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception:
            return False
    
    def delete_schema(self, schema_id: str) -> bool:
        """
        Delete schema definition and associated data.
        
        Args:
            schema_id: Schema to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM schema_definitions 
                WHERE schema_id = ?
            """, (schema_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception:
            return False
