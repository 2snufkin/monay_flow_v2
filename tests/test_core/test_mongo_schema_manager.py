"""
Unit tests for MongoSchemaManager class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any

from src.core.mongo_schema_manager import MongoSchemaManager
from src.models.schema_definition import (
    SchemaDefinition,
    CollectionDefinition,
    AttributeDefinition,
    IndexDefinition,
)


@pytest.mark.unit
class TestMongoSchemaManager:
    """Test cases for MongoSchemaManager class."""

    def setup_method(self):
        """Setup for each test method."""
        self.schema_manager = MongoSchemaManager()

        # Mock settings
        self.schema_manager._settings = Mock()
        self.schema_manager._settings.database.mongo_url = "mongodb://test"

        # Mock MongoDB client
        self.mock_client = Mock()
        self.mock_db = Mock()
        self.mock_collection = Mock()

        # Mock the __getitem__ method properly
        self.mock_client.__getitem__ = Mock(return_value=self.mock_db)
        self.mock_db.__getitem__ = Mock(return_value=self.mock_collection)

        self.schema_manager._client = self.mock_client
        self.schema_manager._metadata_db = self.mock_db

    def test_create_schema_success(self):
        """Test successful schema creation."""
        # Mock data
        schema_name = "Test Schema"
        database_name = "test_schema"
        collection_name = "main_data"
        collection_description = "Main data collection"
        excel_columns = ["Name", "Email", "Amount"]

        normalized_attrs = {
            "Name": AttributeDefinition(
                field_name="name",
                data_type="String",
                description="Customer name",
                is_required=True,
            ),
            "Email": AttributeDefinition(
                field_name="email",
                data_type="String",
                description="Customer email",
                is_required=True,
            ),
        }

        suggested_indexes = [
            IndexDefinition(
                field_names=["email"],
                index_type="unique",
                reason="Email should be unique",
            )
        ]

        duplicate_detection_columns = ["email"]

        # Mock the internal methods
        with (
            patch.object(
                self.schema_manager, "_create_schema_database"
            ) as mock_create_db,
            patch.object(self.schema_manager, "_store_schema_metadata") as mock_store,
        ):
            result = self.schema_manager.create_schema(
                schema_name=schema_name,
                database_name=database_name,
                collection_name=collection_name,
                collection_description=collection_description,
                excel_columns=excel_columns,
                normalized_attributes=normalized_attrs,
                suggested_indexes=suggested_indexes,
                duplicate_detection_columns=duplicate_detection_columns,
            )

            # Verify result
            assert result.startswith("schema_test_schema_")
            assert "schema" in result

            # Verify internal methods were called
            mock_create_db.assert_called_once()
            mock_store.assert_called_once()

    def test_get_all_schemas_success(self):
        """Test successful retrieval of all schemas."""
        # Mock schema documents
        mock_schemas = [
            {
                "schema_id": "schema_1",
                "schema_name": "Schema 1",
                "database_name": "db1",
                "excel_column_names": ["Col1", "Col2"],
                "normalized_attributes": {},
                "suggested_indexes": [],
                "duplicate_detection_columns": [],
                "duplicate_strategy": "skip",
                "data_start_row": 2,
                "collections": [
                    {
                        "name": "main",
                        "description": "Main collection",
                        "created_at": datetime.now(),
                        "document_count": 0,
                        "last_updated": None,
                    }
                ],
                "created_at": datetime.now(),
                "last_used": datetime.now(),
                "usage_count": 0,
            }
        ]

        # Mock the find operation
        self.mock_collection.find.return_value = mock_schemas

        schemas = self.schema_manager.get_all_schemas()

        assert len(schemas) == 1
        assert schemas[0].schema_name == "Schema 1"
        assert schemas[0].database_name == "db1"

    def test_get_schema_by_id_success(self):
        """Test successful retrieval of schema by ID."""
        mock_schema = {
            "schema_id": "schema_1",
            "schema_name": "Test Schema",
            "database_name": "test_db",
            "excel_column_names": ["Col1"],
            "normalized_attributes": {},
            "suggested_indexes": [],
            "duplicate_detection_columns": [],
            "duplicate_strategy": "skip",
            "data_start_row": 2,
            "collections": [],
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "usage_count": 0,
        }

        self.mock_collection.find_one.return_value = mock_schema

        schema = self.schema_manager.get_schema_by_id("schema_1")

        assert schema is not None
        assert schema.schema_name == "Test Schema"
        assert schema.database_name == "test_db"

    def test_get_schema_by_id_not_found(self):
        """Test retrieval of non-existent schema by ID."""
        self.mock_collection.find_one.return_value = None

        schema = self.schema_manager.get_schema_by_id("nonexistent")

        assert schema is None

    def test_add_collection_to_schema_success(self):
        """Test successful addition of collection to schema."""
        # Mock existing schema
        mock_schema = {
            "schema_id": "schema_1",
            "schema_name": "Test Schema",
            "database_name": "test_db",
            "excel_column_names": ["Col1", "Col2"],
            "normalized_attributes": {},
            "suggested_indexes": [],
            "duplicate_detection_columns": [],
            "duplicate_strategy": "skip",
            "data_start_row": 2,
            "collections": [
                {
                    "name": "existing",
                    "description": "Existing collection",
                    "created_at": datetime.now(),
                    "document_count": 0,
                    "last_updated": None,
                }
            ],
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "usage_count": 0,
        }

        self.mock_collection.find_one.return_value = mock_schema

        # Mock the update operation
        self.mock_collection.update_one.return_value = Mock(modified_count=1)

        result = self.schema_manager.add_collection_to_schema(
            "schema_1", "new_collection", "New collection description"
        )

        assert result is True
        self.mock_collection.update_one.assert_called_once()

    def test_delete_collection_from_schema_success(self):
        """Test successful deletion of collection from schema."""
        # Mock existing schema
        mock_schema = {
            "schema_id": "schema_1",
            "schema_name": "Test Schema",
            "database_name": "test_db",
            "excel_column_names": ["Col1", "Col2"],
            "normalized_attributes": {},
            "suggested_indexes": [],
            "duplicate_detection_columns": [],
            "duplicate_strategy": "skip",
            "data_start_row": 2,
            "collections": [
                {
                    "name": "to_delete",
                    "description": "Collection to delete",
                    "created_at": datetime.now(),
                    "document_count": 0,
                    "last_updated": None,
                }
            ],
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "usage_count": 0,
        }

        self.mock_collection.find_one.return_value = mock_schema

        # Mock the update operation
        self.mock_collection.update_one.return_value = Mock(modified_count=1)

        result = self.schema_manager.delete_collection_from_schema(
            "schema_1", "to_delete"
        )

        assert result is True
        self.mock_collection.update_one.assert_called_once()

    def test_rename_collection_in_schema_success(self):
        """Test successful renaming of collection in schema."""
        # Mock existing schema
        mock_schema = {
            "schema_id": "schema_1",
            "schema_name": "Test Schema",
            "database_name": "test_db",
            "excel_column_names": ["Col1", "Col2"],
            "normalized_attributes": {},
            "suggested_indexes": [],
            "duplicate_detection_columns": [],
            "duplicate_strategy": "skip",
            "data_start_row": 2,
            "collections": [
                {
                    "name": "old_name",
                    "description": "Collection to rename",
                    "created_at": datetime.now(),
                    "document_count": 0,
                    "last_updated": None,
                }
            ],
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "usage_count": 0,
        }

        self.mock_collection.find_one.return_value = mock_schema

        # Mock the update operation
        self.mock_collection.update_one.return_value = Mock(modified_count=1)

        result = self.schema_manager.rename_collection_in_schema(
            "schema_1", "old_name", "new_name"
        )

        assert result is True
        self.mock_collection.update_one.assert_called_once()

    def test_create_schema_database_success(self):
        """Test successful creation of schema database and collection."""
        # Mock schema and collection
        schema_def = SchemaDefinition(
            schema_id="test_id",
            schema_name="Test Schema",
            database_name="test_db",
            excel_column_names=["Col1"],
            normalized_attributes={},
            suggested_indexes=[],
            duplicate_detection_columns=[],
            duplicate_strategy="skip",
            data_start_row=2,
            collections=[],
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=0,
        )

        collection_def = CollectionDefinition(
            name="main", description="Main collection", created_at=datetime.now()
        )

        # Mock database and collection
        mock_schema_db = Mock()
        mock_schema_collection = Mock()

        self.mock_client.__getitem__.return_value = mock_schema_db
        mock_schema_db.__getitem__ = Mock(return_value=mock_schema_collection)

        # Test without indexes
        self.schema_manager._create_schema_database(schema_def, collection_def)

        # Verify database and collection were accessed
        self.mock_client.__getitem__.assert_called_with("test_db")
        mock_schema_db.__getitem__.assert_called_with("main")

    def test_create_schema_database_with_indexes(self):
        """Test successful creation of schema database with indexes."""
        # Mock schema with indexes
        schema_def = SchemaDefinition(
            schema_id="test_id",
            schema_name="Test Schema",
            database_name="test_db",
            excel_column_names=["Col1"],
            normalized_attributes={},
            suggested_indexes=[
                IndexDefinition(
                    field_names=["email"],
                    index_type="unique",
                    reason="Email should be unique",
                )
            ],
            duplicate_detection_columns=[],
            duplicate_strategy="skip",
            data_start_row=2,
            collections=[],
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=0,
        )

        collection_def = CollectionDefinition(
            name="main", description="Main collection", created_at=datetime.now()
        )

        # Mock database and collection
        mock_schema_db = Mock()
        mock_schema_collection = Mock()

        self.mock_client.__getitem__.return_value = mock_schema_db
        mock_schema_db.__getitem__ = Mock(return_value=mock_schema_collection)

        # Test with indexes
        self.schema_manager._create_schema_database(schema_def, collection_def)

        # Verify index creation was called
        mock_schema_collection.create_index.assert_called_once()

    def test_store_schema_metadata_success(self):
        """Test successful storage of schema metadata."""
        # Mock schema
        schema_def = SchemaDefinition(
            schema_id="test_id",
            schema_name="Test Schema",
            database_name="test_db",
            excel_column_names=["Col1"],
            normalized_attributes={},
            suggested_indexes=[],
            duplicate_detection_columns=[],
            duplicate_strategy="skip",
            data_start_row=2,
            collections=[],
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=0,
        )

        # Mock insert operation
        self.mock_collection.insert_one.return_value = Mock(inserted_id="test_id")

        self.schema_manager._store_schema_metadata(schema_def)

        # Verify insert was called
        self.mock_collection.insert_one.assert_called_once()

    def test_doc_to_schema_definition_success(self):
        """Test successful conversion of document to SchemaDefinition."""
        # Mock document
        mock_doc = {
            "schema_id": "test_id",
            "schema_name": "Test Schema",
            "database_name": "test_db",
            "excel_column_names": ["Col1"],
            "normalized_attributes": {
                "Col1": {
                    "field_name": "col1",
                    "data_type": "String",
                    "description": "Test column",
                    "is_required": False,
                }
            },
            "suggested_indexes": [
                {
                    "field_names": ["col1"],
                    "index_type": "ascending",
                    "reason": "Test index",
                }
            ],
            "duplicate_detection_columns": ["col1"],
            "duplicate_strategy": "skip",
            "data_start_row": 2,
            "collections": [
                {
                    "name": "main",
                    "description": "Main collection",
                    "created_at": datetime.now(),
                    "document_count": 0,
                    "last_updated": None,
                }
            ],
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "usage_count": 0,
        }

        schema = self.schema_manager._doc_to_schema_definition(mock_doc)

        assert schema.schema_id == "test_id"
        assert schema.schema_name == "Test Schema"
        assert schema.database_name == "test_db"
        assert len(schema.collections) == 1
        assert len(schema.normalized_attributes) == 1
        assert len(schema.suggested_indexes) == 1

    def test_close_connection(self):
        """Test closing MongoDB connection."""
        self.schema_manager.close()

        # Verify client close was called
        self.mock_client.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
