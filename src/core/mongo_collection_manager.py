"""
MongoDB Collection Management Module

Handles MongoDB collection creation, indexing, bulk operations, and duplicate detection.
Optimized for Excel data ingestion with performance and reliability features.
"""

from typing import List, Dict, Any, Optional, Tuple, Iterator
from dataclasses import dataclass
from datetime import datetime
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING, IndexModel
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import BulkWriteError, DuplicateKeyError, PyMongoError
import pandas as pd

from config.database_config import get_mongo_database
from models.schema_definition import SchemaDefinition, IndexDefinition
from config.settings import get_settings

logger = logging.getLogger(__name__)

@dataclass
class BulkOperationResult:
    """Result of a bulk operation."""
    inserted_count: int
    modified_count: int
    deleted_count: int
    upserted_count: int
    errors: List[Dict[str, Any]]
    processing_time_ms: int

@dataclass
class DuplicateCheckResult:
    """Result of duplicate detection."""
    is_duplicate: bool
    existing_document_id: Optional[str]
    duplicate_fields: List[str]
    confidence_score: float

class MongoCollectionManager:
    """Manages MongoDB collections for Excel data storage."""
    
    def __init__(self):
        """Initialize MongoDB collection manager."""
        self.settings = get_settings()
        self.database = get_mongo_database()
        self.batch_size = 1000  # Bulk operation batch size
        
    def create_collection(self, collection_name: str, schema_def: SchemaDefinition) -> Collection:
        """
        Create a new MongoDB collection with schema-based configuration.
        
        Args:
            collection_name: Name of the collection to create
            schema_def: Schema definition with index and validation rules
            
        Returns:
            Collection: Created MongoDB collection
        """
        logger.info(f"🏗️ Creating collection: {collection_name}")
        
        try:
            # Get or create collection
            collection = self.database[collection_name]
            
            # Create indexes based on schema definition
            if schema_def.suggested_indexes:
                self._create_indexes(collection, schema_def.suggested_indexes)
            
            # Create duplicate detection index if specified
            if schema_def.duplicate_detection_columns:
                self._create_duplicate_detection_index(collection, schema_def.duplicate_detection_columns)
            
            logger.info(f"✅ Collection '{collection_name}' created successfully")
            return collection
            
        except Exception as e:
            logger.error(f"❌ Failed to create collection '{collection_name}': {e}")
            raise
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        Get existing MongoDB collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection: MongoDB collection
        """
        return self.database[collection_name]
    
    def bulk_insert(self, collection: Collection, documents: List[Dict[str, Any]], 
                   ordered: bool = False) -> BulkOperationResult:
        """
        Perform bulk insert operation with error handling.
        
        Args:
            collection: Target MongoDB collection
            documents: List of documents to insert
            ordered: Whether to perform ordered insertion
            
        Returns:
            BulkOperationResult: Result of bulk operation
        """
        start_time = datetime.now()
        logger.info(f"📦 Bulk inserting {len(documents)} documents")
        
        try:
            # Perform bulk insert
            result = collection.insert_many(documents, ordered=ordered)
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            bulk_result = BulkOperationResult(
                inserted_count=len(result.inserted_ids),
                modified_count=0,
                deleted_count=0,
                upserted_count=0,
                errors=[],
                processing_time_ms=processing_time
            )
            
            logger.info(f"✅ Bulk insert completed: {bulk_result.inserted_count} documents in {processing_time}ms")
            return bulk_result
            
        except BulkWriteError as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Extract successful and failed operations
            inserted_count = e.details.get('nInserted', 0)
            errors = e.details.get('writeErrors', [])
            
            bulk_result = BulkOperationResult(
                inserted_count=inserted_count,
                modified_count=0,
                deleted_count=0,
                upserted_count=0,
                errors=errors,
                processing_time_ms=processing_time
            )
            
            logger.warning(f"⚠️ Bulk insert partially failed: {inserted_count} inserted, {len(errors)} errors")
            return bulk_result
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.error(f"❌ Bulk insert failed: {e}")
            
            return BulkOperationResult(
                inserted_count=0,
                modified_count=0,
                deleted_count=0,
                upserted_count=0,
                errors=[{"error": str(e)}],
                processing_time_ms=processing_time
            )
    
    def bulk_upsert(self, collection: Collection, documents: List[Dict[str, Any]], 
                   duplicate_fields: List[str]) -> BulkOperationResult:
        """
        Perform bulk upsert operation based on duplicate detection fields.
        
        Args:
            collection: Target MongoDB collection
            documents: List of documents to upsert
            duplicate_fields: Fields to use for duplicate detection
            
        Returns:
            BulkOperationResult: Result of bulk operation
        """
        start_time = datetime.now()
        logger.info(f"🔄 Bulk upserting {len(documents)} documents based on {duplicate_fields}")
        
        try:
            from pymongo import UpdateOne
            
            # Prepare bulk operations
            operations = []
            for doc in documents:
                # Create filter based on duplicate detection fields
                filter_query = {field: doc.get(field) for field in duplicate_fields if field in doc}
                
                if filter_query:  # Only proceed if we have filter criteria
                    operation = UpdateOne(
                        filter_query,
                        {"$set": doc},
                        upsert=True
                    )
                    operations.append(operation)
            
            if not operations:
                logger.warning("⚠️ No valid operations to perform")
                return BulkOperationResult(0, 0, 0, 0, [], 0)
            
            # Execute bulk operations
            result = collection.bulk_write(operations, ordered=False)
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            bulk_result = BulkOperationResult(
                inserted_count=result.inserted_count,
                modified_count=result.modified_count,
                deleted_count=result.deleted_count,
                upserted_count=result.upserted_count,
                errors=[],
                processing_time_ms=processing_time
            )
            
            logger.info(f"✅ Bulk upsert completed: {bulk_result.upserted_count} upserted, "
                       f"{bulk_result.modified_count} modified in {processing_time}ms")
            return bulk_result
            
        except BulkWriteError as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Extract results from partial success
            inserted_count = e.details.get('nInserted', 0)
            modified_count = e.details.get('nModified', 0)
            upserted_count = e.details.get('nUpserted', 0)
            errors = e.details.get('writeErrors', [])
            
            bulk_result = BulkOperationResult(
                inserted_count=inserted_count,
                modified_count=modified_count,
                deleted_count=0,
                upserted_count=upserted_count,
                errors=errors,
                processing_time_ms=processing_time
            )
            
            logger.warning(f"⚠️ Bulk upsert partially failed: {upserted_count} upserted, "
                          f"{modified_count} modified, {len(errors)} errors")
            return bulk_result
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.error(f"❌ Bulk upsert failed: {e}")
            
            return BulkOperationResult(
                inserted_count=0,
                modified_count=0,
                deleted_count=0,
                upserted_count=0,
                errors=[{"error": str(e)}],
                processing_time_ms=processing_time
            )
    
    def check_duplicates(self, collection: Collection, document: Dict[str, Any], 
                        duplicate_fields: List[str]) -> DuplicateCheckResult:
        """
        Check if a document is a duplicate based on specified fields.
        
        Args:
            collection: MongoDB collection to check
            document: Document to check for duplicates
            duplicate_fields: Fields to use for duplicate detection
            
        Returns:
            DuplicateCheckResult: Result of duplicate check
        """
        try:
            # Build query based on duplicate detection fields
            query = {}
            available_fields = []
            
            for field in duplicate_fields:
                if field in document and document[field] is not None:
                    query[field] = document[field]
                    available_fields.append(field)
            
            if not query:
                # No fields available for duplicate detection
                return DuplicateCheckResult(
                    is_duplicate=False,
                    existing_document_id=None,
                    duplicate_fields=[],
                    confidence_score=0.0
                )
            
            # Search for existing document
            existing_doc = collection.find_one(query)
            
            if existing_doc:
                # Calculate confidence score based on matching fields
                confidence_score = len(available_fields) / len(duplicate_fields)
                
                return DuplicateCheckResult(
                    is_duplicate=True,
                    existing_document_id=str(existing_doc['_id']),
                    duplicate_fields=available_fields,
                    confidence_score=confidence_score
                )
            else:
                return DuplicateCheckResult(
                    is_duplicate=False,
                    existing_document_id=None,
                    duplicate_fields=[],
                    confidence_score=0.0
                )
                
        except Exception as e:
            logger.error(f"❌ Duplicate check failed: {e}")
            return DuplicateCheckResult(
                is_duplicate=False,
                existing_document_id=None,
                duplicate_fields=[],
                confidence_score=0.0
            )
    
    def delete_batch(self, collection: Collection, batch_id: str) -> int:
        """
        Delete all documents from a specific import batch.
        
        Args:
            collection: MongoDB collection
            batch_id: Batch ID to delete
            
        Returns:
            int: Number of deleted documents
        """
        logger.info(f"🗑️ Deleting batch: {batch_id}")
        
        try:
            result = collection.delete_many({"_batch_id": batch_id})
            deleted_count = result.deleted_count
            
            logger.info(f"✅ Deleted {deleted_count} documents from batch {batch_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to delete batch {batch_id}: {e}")
            raise
    
    def get_collection_stats(self, collection: Collection) -> Dict[str, Any]:
        """
        Get statistics about a collection.
        
        Args:
            collection: MongoDB collection
            
        Returns:
            Dict: Collection statistics
        """
        try:
            stats = self.database.command("collStats", collection.name)
            
            return {
                "document_count": stats.get("count", 0),
                "storage_size": stats.get("storageSize", 0),
                "index_count": stats.get("nindexes", 0),
                "total_index_size": stats.get("totalIndexSize", 0),
                "average_document_size": stats.get("avgObjSize", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {}
    
    def _create_indexes(self, collection: Collection, index_definitions: List[IndexDefinition]) -> None:
        """
        Create indexes based on schema definition.
        
        Args:
            collection: MongoDB collection
            index_definitions: List of index definitions
        """
        logger.info(f"📊 Creating {len(index_definitions)} indexes")
        
        try:
            for index_def in index_definitions:
                # Handle different index types based on index_type
                if index_def.index_type == "unique":
                    # Create unique index on first field
                    collection.create_index(
                        index_def.field_names[0], 
                        unique=True,
                        name=f"idx_{index_def.field_names[0]}_unique"
                    )
                elif index_def.index_type == "ascending":
                    # Create ascending index
                    collection.create_index(
                        [(index_def.field_names[0], ASCENDING)],
                        name=f"idx_{index_def.field_names[0]}_asc"
                    )
                elif index_def.index_type == "descending":
                    # Create descending index
                    collection.create_index(
                        [(index_def.field_names[0], DESCENDING)],
                        name=f"idx_{index_def.field_names[0]}_desc"
                    )
                elif index_def.index_type == "text":
                    # Create text index
                    collection.create_index(
                        [(index_def.field_names[0], "text")],
                        name=f"idx_{index_def.field_names[0]}_text"
                    )
                elif index_def.index_type == "compound":
                    # Create compound index on multiple fields
                    index_spec = [(field, ASCENDING) for field in index_def.field_names]
                    collection.create_index(
                        index_spec,
                        name=f"idx_compound_{'_'.join(index_def.field_names)}"
                    )
                else:
                    # Default to ascending index
                    collection.create_index(
                        [(index_def.field_names[0], ASCENDING)],
                        name=f"idx_{index_def.field_names[0]}_default"
                    )
                
                logger.debug(f"✅ Created index: {index_def.index_type} on {index_def.field_names}")
            
            logger.info(f"✅ Created {len(index_definitions)} indexes")
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
            raise
    
    def _create_duplicate_detection_index(self, collection: Collection, duplicate_fields: List[str]) -> None:
        """
        Create compound index for duplicate detection.
        
        Args:
            collection: MongoDB collection
            duplicate_fields: Fields to include in duplicate detection index
        """
        logger.info(f"🔍 Creating duplicate detection index on fields: {duplicate_fields}")
        
        try:
            # Create compound index for duplicate detection
            index_spec = [(field, ASCENDING) for field in duplicate_fields]
            
            collection.create_index(
                index_spec,
                name="idx_duplicate_detection",
                background=True  # Create index in background
            )
            
            logger.info(f"✅ Created duplicate detection index")
            
        except Exception as e:
            logger.error(f"❌ Failed to create duplicate detection index: {e}")
            # Don't raise - this is not critical for basic functionality
    
    def optimize_collection(self, collection: Collection) -> None:
        """
        Optimize collection performance by analyzing and rebuilding indexes.
        
        Args:
            collection: MongoDB collection to optimize
        """
        logger.info(f"⚡ Optimizing collection: {collection.name}")
        
        try:
            # Reindex collection
            self.database.command("reIndex", collection.name)
            logger.info(f"✅ Collection {collection.name} optimized")
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize collection: {e}")
            # Don't raise - optimization is not critical
