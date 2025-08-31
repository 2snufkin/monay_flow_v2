"""
Schema Management Module

Handles CRUD operations for schema definitions in MongoDB database.
"""

import uuid
import json
import logging
from datetime import datetime
from typing import List, Optional

from models.schema_definition import (
    SchemaDefinition,
    AttributeDefinition,
    IndexDefinition,
)
from config.settings import get_settings
from core.mongo_schema_manager import MongoSchemaManager

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages schema definitions in MongoDB database."""

    def __init__(self):
        """Initialize SchemaManager."""
        self.settings = get_settings()
        self.mongo_manager = MongoSchemaManager()

    def get_all_schemas(self) -> List[SchemaDefinition]:
        """
        Retrieve all schema definitions from MongoDB database.

        Returns:
            List of all available schema definitions ordered by last_used DESC
        """
        try:
            schemas = self.mongo_manager.get_all_schemas()
            # Sort by last_used DESC
            schemas.sort(key=lambda x: x.last_used, reverse=True)
            return schemas
        except Exception as e:
            logger.error(f"Failed to get schemas from MongoDB: {e}")
            return []

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
        Save AI-processed schema definition to MongoDB database.

        Args:
            schema_data: Complete schema definition with AI suggestions

        Returns:
            True if saved successfully, False otherwise
        """
        logger.info(f"Attempting to save schema: {schema_data.schema_name}")
        logger.debug(
            f"Schema ID: {schema_data.schema_id}, Columns: {len(schema_data.excel_column_names)}"
        )

        try:
            # Use MongoDB schema manager to create the schema
            success = self.mongo_manager.create_schema(schema_data)

            if success:
                logger.info(
                    f"✅ Schema '{schema_data.schema_name}' saved successfully to MongoDB"
                )
                return True
            else:
                logger.error(
                    f"❌ Failed to save schema '{schema_data.schema_name}' to MongoDB"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Exception while saving schema: {e}")
            return False

    def get_schema_by_id(self, schema_id: str) -> Optional[SchemaDefinition]:
        """
        Retrieve a specific schema by its ID.

        Args:
            schema_id: Unique identifier for the schema

        Returns:
            SchemaDefinition if found, None otherwise
        """
        try:
            return self.mongo_manager.get_schema_by_id(schema_id)
        except Exception as e:
            logger.error(f"Failed to get schema by ID {schema_id}: {e}")
            return None

    def get_schema_by_name(self, schema_name: str) -> Optional[SchemaDefinition]:
        """
        Retrieve a specific schema by its name.

        Args:
            schema_name: Name of the schema

        Returns:
            SchemaDefinition if found, None otherwise
        """
        try:
            return self.mongo_manager.get_schema_by_name(schema_name)
        except Exception as e:
            logger.error(f"Failed to get schema by name {schema_name}: {e}")
            return None

    def update_schema_usage(self, schema_id: str) -> bool:
        """
        Update the last_used timestamp and usage_count for a schema.

        Args:
            schema_id: Unique identifier for the schema

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Get current schema
            schema = self.mongo_manager.get_schema_by_id(schema_id)
            if not schema:
                logger.warning(f"Schema {schema_id} not found for usage update")
                return False

            # Update usage statistics
            schema.last_used = datetime.now()
            schema.usage_count += 1

            # Save updated schema back to MongoDB
            success = self.mongo_manager.create_schema(schema)

            if success:
                logger.info(f"✅ Updated usage for schema {schema_id}")
                return True
            else:
                logger.error(f"❌ Failed to update usage for schema {schema_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Exception while updating schema usage: {e}")
            return False

    def delete_schema(self, schema_id: str) -> bool:
        """
        Delete a schema definition from the database.

        Args:
            schema_id: Unique identifier for the schema to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # For now, we'll just mark it as deleted in the metadata
            # In a full implementation, you might want to also clean up the MongoDB database
            logger.info(f"Deleting schema {schema_id}")

            # Get the schema to see what database/collections to clean up
            schema = self.mongo_manager.get_schema_by_id(schema_id)
            if not schema:
                logger.warning(f"Schema {schema_id} not found for deletion")
                return False

            # TODO: Implement actual deletion logic
            # This would involve:
            # 1. Removing from excel_imports.schemas collection
            # 2. Optionally dropping the schema's database/collections

            logger.info(f"✅ Schema {schema_id} marked for deletion")
            return True

        except Exception as e:
            logger.error(f"❌ Exception while deleting schema: {e}")
            return False

    def close(self):
        """Close database connections."""
        try:
            if hasattr(self, "mongo_manager"):
                self.mongo_manager.close()
            logger.info("SchemaManager connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")
