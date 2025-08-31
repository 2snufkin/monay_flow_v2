#!/usr/bin/env python3
"""
MongoDB Schema Manager

Handles the creation and management of MongoDB databases and collections
for the MoneyFlow Data Ingestion App.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from models.schema_definition import SchemaDefinition, CollectionDefinition, AttributeDefinition, IndexDefinition
from config.settings import get_settings

logger = logging.getLogger(__name__)


class MongoSchemaManager:
    """Manages MongoDB schemas, databases, and collections."""

    def __init__(self):
        """Initialize the MongoDB schema manager."""
        self.settings = get_settings()
        self.client = MongoClient(self.settings.database.mongo_url)
        self.metadata_db = self.client.excel_schemas

    def create_schema(self, schema_def: SchemaDefinition) -> bool:
        """Create a new schema with its dedicated MongoDB database and collection."""
        try:
            logger.info(f"Creating schema: {schema_def.schema_name}")

            # 1. Create the dedicated database for this schema
            db_name = schema_def.database_name
            if not db_name:
                logger.error("Database name is required")
                return False

            # 2. Get or create the database
            db = self.client[db_name]

            # 3. Create collections based on schema
            for collection_def in schema_def.collections:
                collection_name = collection_def.name
                if not collection_name:
                    logger.error("Collection name is required")
                    continue

                # Create the collection
                collection = db[collection_name]

                # Create indexes based on schema
                self._create_indexes(collection, schema_def.suggested_indexes)

                logger.info(f"Created collection: {db_name}.{collection_name}")

            # 4. Save schema metadata in excel_schemas.schemas collection
            schema_doc = self._schema_definition_to_doc(schema_def)
            self.metadata_db.schemas.insert_one(schema_doc)

            logger.info(f"Schema metadata saved to excel_schemas.schemas")
            return True

        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False

    def _create_indexes(self, collection: Collection, suggested_indexes: List) -> None:
        """Create indexes for a collection."""
        try:
            for index in suggested_indexes:
                if hasattr(index, "field_names") and hasattr(index, "index_type"):
                    # Create compound index
                    index_fields = [(field, 1) for field in index.field_names]
                    collection.create_index(index_fields)
                    logger.info(f"Created index: {index_fields}")
                else:
                    # Handle simple field names
                    if isinstance(index, str):
                        collection.create_index([(index, 1)])
                        logger.info(f"Created index: {index}")
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")

    def _schema_definition_to_doc(self, schema_def: SchemaDefinition) -> Dict[str, Any]:
        """Convert SchemaDefinition to MongoDB document."""
        return {
            "schema_id": schema_def.schema_id,
            "schema_name": schema_def.schema_name,
            "database_name": schema_def.database_name,
            "excel_column_names": schema_def.excel_column_names,
            "normalized_attributes": self._serialize_attributes(
                schema_def.normalized_attributes
            ),
            "suggested_indexes": self._serialize_indexes(schema_def.suggested_indexes),
            "duplicate_detection_columns": schema_def.duplicate_detection_columns,
            "duplicate_strategy": schema_def.duplicate_strategy,
            "data_start_row": schema_def.data_start_row,
            "collections": [
                {
                    "name": col.name,
                    "description": col.description,
                    "created_at": col.created_at,
                    "document_count": col.document_count,
                    "last_updated": col.last_updated,
                }
                for col in schema_def.collections
            ],
            "created_at": schema_def.created_at,
            "last_used": schema_def.last_used,
            "usage_count": schema_def.usage_count,
        }

    def _serialize_attributes(self, attributes: Dict) -> Dict:
        """Serialize attribute definitions for MongoDB storage."""
        serialized = {}
        for key, attr in attributes.items():
            if hasattr(attr, "__dict__"):
                serialized[key] = attr.__dict__
            else:
                serialized[key] = str(attr)
        return serialized

    def _serialize_indexes(self, indexes: List) -> List:
        """Serialize index definitions for MongoDB storage."""
        serialized = []
        for idx in indexes:
            if hasattr(idx, "__dict__"):
                serialized.append(idx.__dict__)
            else:
                serialized.append(str(idx))
        return serialized

    def get_all_schemas(self) -> List[SchemaDefinition]:
        """Get all schemas from MongoDB."""
        try:
            schemas = []
            cursor = self.metadata_db.schemas.find()

            for doc in cursor:
                schema = self._doc_to_schema_definition(doc)
                if schema:
                    schemas.append(schema)

            return schemas

        except Exception as e:
            logger.error(f"Failed to get schemas: {e}")
            return []

    def get_schema_by_id(self, schema_id: str) -> Optional[SchemaDefinition]:
        """Get a schema by ID."""
        try:
            doc = self.metadata_db.schemas.find_one({"schema_id": schema_id})
            if doc:
                return self._doc_to_schema_definition(doc)
            return None

        except Exception as e:
            logger.error(f"Failed to get schema by ID: {e}")
            return None

    def get_schema_by_name(self, schema_name: str) -> Optional[SchemaDefinition]:
        """Get a schema by name."""
        try:
            doc = self.metadata_db.schemas.find_one({"schema_name": schema_name})
            if doc:
                return self._doc_to_schema_definition(doc)
            return None

        except Exception as e:
            logger.error(f"Failed to get schema by name: {e}")
            return None

    def _doc_to_schema_definition(
        self, doc: Dict[str, Any]
    ) -> Optional[SchemaDefinition]:
        """Convert MongoDB document to SchemaDefinition."""
        try:
            # This is a simplified conversion - you may need to adjust based on your models
            collections = []
            for col_doc in doc.get("collections", []):
                collection = CollectionDefinition(
                    name=col_doc.get("name", ""),
                    description=col_doc.get("description", ""),
                    created_at=col_doc.get("created_at", datetime.now()),
                    document_count=col_doc.get("document_count", 0),
                    last_updated=col_doc.get("last_updated", datetime.now()),
                )
                collections.append(collection)

            # Convert normalized_attributes from dict to AttributeDefinition objects
            normalized_attributes = {}
            raw_attrs = doc.get("normalized_attributes", {})
            for excel_col, attr_data in raw_attrs.items():
                if isinstance(attr_data, dict):
                    # Convert dict to AttributeDefinition object
                    normalized_attributes[excel_col] = AttributeDefinition(
                        field_name=attr_data.get("field_name", excel_col),
                        data_type=attr_data.get("data_type", "String"),
                        description=attr_data.get("description", ""),
                        is_required=attr_data.get("is_required", False)
                    )
                elif hasattr(attr_data, 'field_name'):
                    # Already an AttributeDefinition object
                    normalized_attributes[excel_col] = attr_data
                else:
                    # Fallback: create basic AttributeDefinition
                    normalized_attributes[excel_col] = AttributeDefinition(
                        field_name=str(excel_col).lower().replace(' ', '_').replace('-', '_'),
                        data_type="String",
                        description=f"Auto-generated field for {excel_col}",
                        is_required=False
                    )

            # Convert suggested_indexes from dict to IndexDefinition objects
            suggested_indexes = []
            raw_indexes = doc.get("suggested_indexes", [])
            for idx_data in raw_indexes:
                if isinstance(idx_data, dict):
                    suggested_indexes.append(IndexDefinition(
                        field_names=idx_data.get("field_names", []),
                        index_type=idx_data.get("index_type", "ascending"),
                        reason=idx_data.get("reason", "Performance optimization")
                    ))
                elif hasattr(idx_data, 'field_names'):
                    # Already an IndexDefinition object
                    suggested_indexes.append(idx_data)

            # Create SchemaDefinition - you'll need to adjust this based on your actual model
            schema = SchemaDefinition(
                schema_id=doc.get("schema_id", ""),
                schema_name=doc.get("schema_name", ""),
                database_name=doc.get("database_name", ""),
                excel_column_names=doc.get("excel_column_names", []),
                normalized_attributes=normalized_attributes,
                suggested_indexes=suggested_indexes,
                duplicate_detection_columns=doc.get("duplicate_detection_columns", []),
                duplicate_strategy=doc.get("duplicate_strategy", "skip"),
                data_start_row=doc.get("data_start_row", 2),
                collections=collections,
                created_at=doc.get("created_at", datetime.now()),
                last_used=doc.get("last_used", datetime.now()),
                usage_count=doc.get("usage_count", 0),
            )

            return schema

        except Exception as e:
            logger.error(f"Failed to convert document to SchemaDefinition: {e}")
            return None

    def add_collection_to_schema(
        self, schema_id: str, collection_def: CollectionDefinition
    ) -> bool:
        """Add a new collection to an existing schema."""
        try:
            # Update schema metadata
            result = self.metadata_db.schemas.update_one(
                {"schema_id": schema_id},
                {
                    "$push": {
                        "collections": {
                            "name": collection_def.name,
                            "description": collection_def.description,
                            "created_at": collection_def.created_at,
                            "document_count": collection_def.document_count,
                            "last_updated": collection_def.last_updated,
                        }
                    }
                },
            )

            if result.modified_count > 0:
                # Create the actual collection in MongoDB
                schema = self.get_schema_by_id(schema_id)
                if schema:
                    db = self.client[schema.database_name]
                    collection = db[collection_def.name]

                    # Create indexes if schema has them
                    if schema.suggested_indexes:
                        self._create_indexes(collection, schema.suggested_indexes)

                    logger.info(
                        f"Added collection {collection_def.name} to schema {schema_id}"
                    )
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to add collection: {e}")
            return False

    def delete_collection_from_schema(
        self, schema_id: str, collection_name: str
    ) -> bool:
        """Delete a collection from a schema."""
        try:
            # Update schema metadata
            result = self.metadata_db.schemas.update_one(
                {"schema_id": schema_id},
                {"$pull": {"collections": {"name": collection_name}}},
            )

            if result.modified_count > 0:
                # Drop the actual collection from MongoDB
                schema = self.get_schema_by_id(schema_id)
                if schema:
                    db = self.client[schema.database_name]
                    db.drop_collection(collection_name)

                    logger.info(
                        f"Deleted collection {collection_name} from schema {schema_id}"
                    )
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False

    def rename_collection_in_schema(
        self, schema_id: str, old_name: str, new_name: str
    ) -> bool:
        """Rename a collection in a schema."""
        try:
            # Update schema metadata
            result = self.metadata_db.schemas.update_one(
                {"schema_id": schema_id, "collections.name": old_name},
                {"$set": {"collections.$.name": new_name}},
            )

            if result.modified_count > 0:
                # Rename the actual collection in MongoDB
                schema = self.get_schema_by_id(schema_id)
                if schema:
                    db = self.client[schema.database_name]
                    db.rename_collection(old_name, new_name)

                    logger.info(
                        f"Renamed collection {old_name} to {new_name} in schema {schema_id}"
                    )
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to rename collection: {e}")
            return False

    def clear_excel_schemas_database(self) -> bool:
        """Clear all data from the excel_schemas database except schemas collection."""
        try:
            # Get all collections in excel_schemas database
            collections = self.metadata_db.list_collection_names()

            for collection_name in collections:
                if collection_name != "schemas":  # Keep schemas collection
                    self.metadata_db.drop_collection(collection_name)
                    logger.info(f"Dropped collection: {collection_name}")

            logger.info("Cleared excel_schemas database")
            return True

        except Exception as e:
            logger.error(f"Failed to clear excel_schemas database: {e}")
            return False

    def close(self):
        """Close the MongoDB client connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB client connection closed")
