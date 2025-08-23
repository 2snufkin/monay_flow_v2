"""
Unit tests for MongoCollectionManager class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from src.core.mongo_manager import MongoCollectionManager
from src.models.schema_definition import SchemaDefinition, IndexDefinition
from src.models.ingestion_result import BulkInsertResult, RollbackResult, CollectionStats


@pytest.mark.unit
class TestMongoCollectionManager:
    """Test cases for MongoCollectionManager class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mongo_manager = MongoCollectionManager()
    
    @patch('src.core.mongo_manager.get_mongo_database')
    def test_create_collection_success(self, mock_get_db, sample_schema_definition):
        """Test successful collection creation."""
        mock_db = Mock()
        mock_db.list_collection_names.return_value = []  # Collection doesn't exist
        mock_get_db.return_value = mock_db
        
        # Create schema definition object  
        from datetime import datetime
        schema_def = SchemaDefinition(
            schema_id="test_id",
            schema_name="Test Schema",
            original_columns=["Col1", "Col2"],
            normalized_attributes={},
            suggested_indexes=[],
            duplicate_detection_columns=[],
            duplicate_strategy="skip",
            data_start_row=2,
            mongodb_collection_name="test_collection",
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=0
        )
        
        result = self.mongo_manager.create_collection("test_collection", schema_def)
        
        assert result is True
        mock_db.create_collection.assert_called_once_with("test_collection")
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_create_indexes_success(self, mock_get_collection):
        """Test successful index creation."""
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection
        
        index_definitions = [
            IndexDefinition(field="email", type="unique", reason="Unique identifier"),
            IndexDefinition(field="date", type="ascending", reason="Date queries")
        ]
        
        result = self.mongo_manager.create_indexes("test_collection", index_definitions)
        
        assert result is True
        # Should call create_index for each definition
        assert mock_collection.create_index.call_count == 2
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_check_document_exists_found(self, mock_get_collection, sample_schema_definition):
        """Test document existence check when document exists."""
        mock_collection = Mock()
        mock_collection.find_one.return_value = {"_id": "existing_id", "email": "test@email.com"}
        mock_get_collection.return_value = mock_collection
        
        schema_def = SchemaDefinition(
            schema_id="test_id",
            schema_name="Test Schema",
            original_columns=["Email"],
            normalized_attributes={
                "Email": {
                    "field_name": "email",
                    "data_type": "String",
                    "description": "Email field"
                }
            },
            suggested_indexes=[],
            duplicate_detection_columns=["email"],
            duplicate_strategy="skip",
            data_start_row=2,
            mongodb_collection_name="test_collection",
            created_at=None,
            last_used=None,
            usage_count=0
        )
        
        raw_data = {"Email": "test@email.com"}
        
        result = self.mongo_manager.check_document_exists("test_collection", raw_data, schema_def)
        
        assert result is not None
        assert result["email"] == "test@email.com"
        mock_collection.find_one.assert_called_once()
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_check_document_exists_not_found(self, mock_get_collection, sample_schema_definition):
        """Test document existence check when document doesn't exist."""
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        mock_get_collection.return_value = mock_collection
        
        schema_def = SchemaDefinition(
            schema_id="test_id",
            schema_name="Test Schema",
            original_columns=["Email"],
            normalized_attributes={
                "Email": {
                    "field_name": "email",
                    "data_type": "String",
                    "description": "Email field"
                }
            },
            suggested_indexes=[],
            duplicate_detection_columns=["email"],
            duplicate_strategy="skip",
            data_start_row=2,
            mongodb_collection_name="test_collection",
            created_at=None,
            last_used=None,
            usage_count=0
        )
        
        raw_data = {"Email": "nonexistent@email.com"}
        
        result = self.mongo_manager.check_document_exists("test_collection", raw_data, schema_def)
        
        assert result is None
        mock_collection.find_one.assert_called_once()
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_insert_document_with_metadata_success(self, mock_get_collection):
        """Test successful document insertion with metadata."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.inserted_id = "new_document_id"
        mock_collection.insert_one.return_value = mock_result
        mock_get_collection.return_value = mock_collection
        
        document = {"email": "test@email.com", "name": "Test User"}
        batch_id = "batch_123"
        row_number = 5
        
        result = self.mongo_manager.insert_document_with_metadata(
            "test_collection", document, batch_id, row_number
        )
        
        assert result == "new_document_id"
        mock_collection.insert_one.assert_called_once()
        
        # Check that metadata was added to document
        inserted_doc = mock_collection.insert_one.call_args[0][0]
        assert "_ingestion_metadata" in inserted_doc
        assert inserted_doc["_ingestion_metadata"]["batch_id"] == batch_id
        assert inserted_doc["_ingestion_metadata"]["original_row"] == row_number
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_rollback_batch_success(self, mock_get_collection):
        """Test successful batch rollback."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.deleted_count = 5
        mock_collection.delete_many.return_value = mock_result
        mock_get_collection.return_value = mock_collection
        
        result = self.mongo_manager.rollback_batch("test_collection", "batch_123")
        
        assert isinstance(result, RollbackResult)
        assert result.success is True
        assert result.documents_deleted == 5
        
        # Should delete documents with matching batch_id
        mock_collection.delete_many.assert_called_once()
        delete_query = mock_collection.delete_many.call_args[0][0]
        assert "_ingestion_metadata.batch_id" in delete_query
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_get_collection_stats(self, mock_get_collection):
        """Test getting collection statistics."""
        mock_collection = Mock()
        mock_collection.count_documents.return_value = 100
        mock_collection.list_indexes.return_value = [
            {"name": "_id_", "key": {"_id": 1}},
            {"name": "email_1", "key": {"email": 1}}
        ]
        
        # Mock stats command
        mock_db = Mock()
        mock_db.command.return_value = {
            "size": 50000,
            "avgObjSize": 500.0
        }
        mock_collection.database = mock_db
        mock_get_collection.return_value = mock_collection
        
        result = self.mongo_manager.get_collection_stats("test_collection")
        
        assert isinstance(result, CollectionStats)
        assert result.document_count == 100
        assert result.index_count == 2
        assert result.size_bytes == 50000
        assert result.average_object_size == 500.0
    
    def test_mongo_manager_initialization(self):
        """Test MongoCollectionManager initialization."""
        manager = MongoCollectionManager()
        assert manager is not None
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_bulk_insert_documents_success(self, mock_get_collection):
        """Test successful bulk document insertion."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.inserted_count = 3
        mock_collection.insert_many.return_value = mock_result
        mock_get_collection.return_value = mock_collection
        
        documents = [
            {"email": "user1@email.com", "name": "User 1"},
            {"email": "user2@email.com", "name": "User 2"},
            {"email": "user3@email.com", "name": "User 3"}
        ]
        
        result = self.mongo_manager.bulk_insert_documents("test_collection", documents)
        
        assert isinstance(result, BulkInsertResult)
        assert result.inserted_count == 3
        assert result.error_count == 0
        mock_collection.insert_many.assert_called_once()
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_update_document_success(self, mock_get_collection):
        """Test successful document update."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.modified_count = 1
        mock_collection.update_one.return_value = mock_result
        mock_get_collection.return_value = mock_collection
        
        filter_keys = {"email": "test@email.com"}
        document = {"name": "Updated Name", "email": "test@email.com"}
        batch_id = "batch_123"
        
        result = self.mongo_manager.update_document(
            "test_collection", filter_keys, document, batch_id
        )
        
        assert result is True
        mock_collection.update_one.assert_called_once()
    
    @patch('src.core.mongo_manager.get_mongo_collection')
    def test_create_indexes_error_handling(self, mock_get_collection):
        """Test error handling in index creation."""
        mock_collection = Mock()
        mock_collection.create_index.side_effect = Exception("Index creation failed")
        mock_get_collection.return_value = mock_collection
        
        index_definitions = [
            IndexDefinition(field="email", type="unique", reason="Test")
        ]
        
        result = self.mongo_manager.create_indexes("test_collection", index_definitions)
        
        assert result is False
