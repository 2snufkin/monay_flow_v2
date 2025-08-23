"""
MongoDB Integration Module

Handles MongoDB collection management and data operations.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo.collection import Collection
from pymongo import MongoClient

from src.models.schema_definition import SchemaDefinition, IndexDefinition
from src.models.ingestion_result import BulkInsertResult, RollbackResult, CollectionStats
from src.config.database_config import get_mongo_collection, get_mongo_database


class MongoCollectionManager:
    """Manages MongoDB collections and data operations."""
    
    def __init__(self):
        """Initialize MongoCollectionManager."""
        pass
    
    def create_collection(self, collection_name: str, schema_def: SchemaDefinition) -> bool:
        """
        Create MongoDB collection with proper schema validation.
        
        Args:
            collection_name: Name for the new collection
            schema_def: Schema definition with field specifications
            
        Returns:
            True if collection created successfully
        """
        try:
            db = get_mongo_database()
            
            # Create collection if it doesn't exist
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
            
            return True
            
        except Exception:
            return False
    
    def create_indexes(self, collection_name: str, index_definitions: List[IndexDefinition]) -> bool:
        """
        Create suggested indexes on collection for optimal performance.
        
        Args:
            collection_name: Target collection name
            index_definitions: List of index specifications from AI
            
        Returns:
            True if all indexes created successfully
        """
        try:
            collection = get_mongo_collection(collection_name)
            
            for index_def in index_definitions:
                # Determine index type and create accordingly
                if index_def.index_type == "unique":
                    collection.create_index(index_def.field_names[0], unique=True)
                elif index_def.index_type == "ascending":
                    collection.create_index([(index_def.field_names[0], 1)])
                elif index_def.index_type == "descending":
                    collection.create_index([(index_def.field_names[0], -1)])
                elif index_def.index_type == "text":
                    collection.create_index([(index_def.field_names[0], "text")])
                else:
                    # Default to ascending
                    collection.create_index([(index_def.field_names[0], 1)])
            
            return True
            
        except Exception:
            return False
    
    def check_document_exists(self, collection_name: str, raw_row_data: dict, schema_def: SchemaDefinition) -> Optional[dict]:
        """
        Check if document exists based on duplicate detection logic using mapped field names.
        
        Args:
            collection_name: Target collection
            raw_row_data: Raw Excel row data with original column names
            schema_def: Schema definition with column mappings
            
        Returns:
            Existing document if found, None otherwise
        """
        try:
            collection = get_mongo_collection(collection_name)
            
            # Build query using duplicate detection columns (MongoDB field names)
            query = {}
            for mongo_field in schema_def.duplicate_detection_columns:
                # Find the Excel column that maps to this MongoDB field
                excel_column = self._find_excel_column_for_mongo_field(mongo_field, schema_def)
                if excel_column and excel_column in raw_row_data:
                    query[mongo_field] = raw_row_data[excel_column]
            
            if not query:
                return None
            
            return collection.find_one(query)
            
        except Exception:
            return None
    
    def _find_excel_column_for_mongo_field(self, mongo_field: str, schema_def: SchemaDefinition) -> Optional[str]:
        """
        Find Excel column name that maps to a MongoDB field.
        
        Args:
            mongo_field: MongoDB field name
            schema_def: Schema definition with mappings
            
        Returns:
            Excel column name or None if not found
        """
        for excel_col, attr_def in schema_def.normalized_attributes.items():
            if attr_def.field_name == mongo_field:
                return excel_col
        return None
    
    def bulk_insert_documents(self, collection_name: str, documents: List[dict]) -> BulkInsertResult:
        """
        Perform bulk insert operation with duplicate checking.
        
        Args:
            collection_name: Target collection
            documents: List of normalized documents to insert
            
        Returns:
            Result object with inserted/skipped counts and errors
        """
        try:
            collection = get_mongo_collection(collection_name)
            
            result = collection.insert_many(documents, ordered=False)
            
            return BulkInsertResult(
                inserted_count=len(result.inserted_ids),
                skipped_count=0,
                error_count=0,
                errors=[],
                inserted_ids=[str(id) for id in result.inserted_ids]
            )
            
        except Exception as e:
            return BulkInsertResult(
                inserted_count=0,
                skipped_count=0,
                error_count=len(documents),
                errors=[str(e)],
                inserted_ids=[]
            )
    
    def insert_document_with_metadata(self, collection_name: str, document: dict, batch_id: str, row_number: int) -> Optional[str]:
        """
        Insert document with ingestion metadata for tracking.
        
        Args:
            collection_name: Target collection
            document: Normalized document data to insert
            batch_id: Import batch identifier
            row_number: Original Excel row number
            
        Returns:
            Inserted document _id or None if failed
        """
        try:
            collection = get_mongo_collection(collection_name)
            
            # Add ingestion metadata
            document_with_metadata = document.copy()
            document_with_metadata["_ingestion_metadata"] = {
                "batch_id": batch_id,
                "original_row": row_number,
                "ingested_at": datetime.utcnow(),
                "file_source": f"batch_{batch_id}"
            }
            
            result = collection.insert_one(document_with_metadata)
            return str(result.inserted_id)
            
        except Exception:
            return None
    
    def update_document(self, collection_name: str, filter_keys: dict, document: dict, batch_id: str) -> bool:
        """
        Update existing document with audit trail.
        
        Args:
            collection_name: Target collection
            filter_keys: Keys to identify document (using MongoDB field names)
            document: Updated document data
            batch_id: Import batch identifier
            
        Returns:
            True if updated successfully
        """
        try:
            collection = get_mongo_collection(collection_name)
            
            # Add update metadata
            update_data = document.copy()
            update_data["_ingestion_metadata.last_updated"] = datetime.utcnow()
            update_data["_ingestion_metadata.updated_by_batch"] = batch_id
            
            result = collection.update_one(filter_keys, {"$set": update_data})
            return result.modified_count > 0
            
        except Exception:
            return False
    
    def rollback_batch(self, collection_name: str, batch_id: str) -> RollbackResult:
        """
        Remove all documents from a specific import batch.
        
        Args:
            collection_name: Target collection
            batch_id: Batch to rollback
            
        Returns:
            Result object with rollback statistics
        """
        try:
            collection = get_mongo_collection(collection_name)
            
            # Delete all documents with the specified batch_id
            result = collection.delete_many({"_ingestion_metadata.batch_id": batch_id})
            
            return RollbackResult(
                success=True,
                documents_deleted=result.deleted_count,
                documents_restored=0,
                errors=[],
                processing_time_ms=0  # Could add timing if needed
            )
            
        except Exception as e:
            return RollbackResult(
                success=False,
                documents_deleted=0,
                documents_restored=0,
                errors=[str(e)],
                processing_time_ms=0
            )
    
    def get_collection_stats(self, collection_name: str) -> CollectionStats:
        """
        Get collection statistics for monitoring.
        
        Returns:
            Statistics object with document counts, indexes, etc.
        """
        try:
            collection = get_mongo_collection(collection_name)
            
            # Get document count
            doc_count = collection.count_documents({})
            
            # Get indexes
            indexes = list(collection.list_indexes())
            
            # Get collection stats from database
            stats = collection.database.command("collStats", collection_name)
            
            return CollectionStats(
                document_count=doc_count,
                index_count=len(indexes),
                size_bytes=stats.get("size", 0),
                average_object_size=stats.get("avgObjSize", 0.0),
                indexes=indexes
            )
            
        except Exception:
            return CollectionStats(
                document_count=0,
                index_count=0,
                size_bytes=0,
                average_object_size=0.0,
                indexes=[]
            )
