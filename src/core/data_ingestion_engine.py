"""
Data Ingestion Engine Module

Orchestrates the complete data ingestion pipeline from Excel files to MongoDB.
Handles schema processing, data transformation, duplicate detection, and quality validation.
"""

import uuid
from typing import List, Dict, Any, Optional, Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging
import pandas as pd

from core.excel_processor import ExcelProcessor, ExcelFileInfo
from core.mongo_collection_manager import MongoCollectionManager, BulkOperationResult
from core.schema_manager import SchemaManager
from models.schema_definition import SchemaDefinition
from config.database_config import get_sqlite_connection

logger = logging.getLogger(__name__)

@dataclass
class ImportBatch:
    """Information about an import batch."""
    batch_id: str
    schema_id: str
    file_name: str
    file_hash: str
    data_start_row: int
    total_rows: int
    created_at: datetime
    status: str = "in_progress"

@dataclass
class ImportProgress:
    """Progress information for an import operation."""
    batch_id: str
    total_rows: int
    processed_rows: int
    inserted_rows: int
    skipped_rows: int
    error_rows: int
    current_operation: str
    processing_time_ms: int
    estimated_remaining_ms: int
    progress_percentage: float

@dataclass
class ImportResult:
    """Final result of an import operation."""
    batch_id: str
    success: bool
    total_rows: int
    inserted_rows: int
    modified_rows: int
    skipped_rows: int
    error_rows: int
    processing_time_ms: int
    error_messages: List[str]
    quality_issues: List[Dict[str, Any]]

class DataIngestionEngine:
    """Orchestrates the complete data ingestion pipeline."""
    
    def __init__(self):
        """Initialize the data ingestion engine."""
        self.excel_processor = ExcelProcessor()
        self.mongo_manager = MongoCollectionManager()
        self.schema_manager = SchemaManager()
        self.current_batch: Optional[ImportBatch] = None
        self.progress_callback: Optional[Callable[[ImportProgress], None]] = None
        
    def set_progress_callback(self, callback: Callable[[ImportProgress], None]) -> None:
        """
        Set callback function for progress updates.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
    
    def import_excel_file(self, file_path: Path, schema_def: SchemaDefinition, 
                         duplicate_strategy: str = "skip") -> ImportResult:
        """
        Import Excel file using specified schema definition.
        
        Args:
            file_path: Path to Excel file
            schema_def: Schema definition for processing
            duplicate_strategy: How to handle duplicates ("skip", "update", "upsert")
            
        Returns:
            ImportResult: Complete import results
        """
        start_time = datetime.now()
        logger.info(f"🚀 Starting Excel import: {file_path}")
        logger.info(f"📋 Using schema: {schema_def.schema_name}")
        logger.info(f"🔄 Duplicate strategy: {duplicate_strategy}")
        
        try:
            # Step 1: Validate file
            if not self.excel_processor.validate_file(file_path):
                raise ValueError(f"Invalid Excel file: {file_path}")
            
            # Step 2: Get file information
            file_info = self.excel_processor.get_file_info(file_path)
            
            # Step 3: Create import batch
            batch = self._create_import_batch(file_info, schema_def)
            self.current_batch = batch
            
            # Step 4: Create MongoDB collection
            collection = self.mongo_manager.create_collection(
                schema_def.mongodb_collection_name, 
                schema_def
            )
            
            # Step 5: Process data in chunks
            result = self._process_data_chunks(
                file_path, 
                schema_def, 
                collection, 
                duplicate_strategy,
                file_info
            )
            
            # Step 6: Update batch status
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._update_batch_status(batch.batch_id, "completed", processing_time)
            
            # Step 7: Update schema usage
            self.schema_manager.update_schema_usage(schema_def.schema_id)
            
            logger.info(f"✅ Import completed successfully in {processing_time}ms")
            logger.info(f"📊 Results: {result.inserted_rows} inserted, {result.skipped_rows} skipped, {result.error_rows} errors")
            
            return result
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.error(f"❌ Import failed: {e}")
            
            if self.current_batch and hasattr(self.current_batch, 'batch_id'):
                self._update_batch_status(self.current_batch.batch_id, "failed", processing_time)
            
            return ImportResult(
                batch_id=self.current_batch.batch_id if self.current_batch else "unknown",
                success=False,
                total_rows=0,
                inserted_rows=0,
                modified_rows=0,
                skipped_rows=0,
                error_rows=0,
                processing_time_ms=processing_time,
                error_messages=[str(e)],
                quality_issues=[]
            )
    
    def preview_import(self, file_path: Path, schema_def: SchemaDefinition, 
                      num_rows: int = 5) -> pd.DataFrame:
        """
        Preview how Excel data will be imported with the given schema.
        
        Args:
            file_path: Path to Excel file
            schema_def: Schema definition for processing
            num_rows: Number of rows to preview
            
        Returns:
            pd.DataFrame: Transformed preview data
        """
        logger.info(f"👀 Previewing import for {num_rows} rows")
        
        try:
            # Get raw preview data
            raw_data = self.excel_processor.preview_data(
                file_path, 
                start_row=schema_def.data_start_row,
                num_rows=num_rows
            )
            
            # Transform data using schema
            transformed_data = self._transform_dataframe(raw_data, schema_def)
            
            logger.info(f"✅ Preview generated: {len(transformed_data)} rows")
            return transformed_data
            
        except Exception as e:
            logger.error(f"❌ Preview failed: {e}")
            raise
    
    def rollback_import(self, batch_id: str) -> bool:
        """
        Rollback a completed import by removing all documents from the batch.
        
        Args:
            batch_id: Batch ID to rollback
            
        Returns:
            bool: True if rollback successful
        """
        logger.info(f"🔄 Rolling back import batch: {batch_id}")
        
        try:
            # Get batch information
            batch_info = self._get_batch_info(batch_id)
            if not batch_info:
                logger.error(f"❌ Batch not found: {batch_id}")
                return False
            
            # Get schema definition
            schema_def = self.schema_manager.get_schema_by_id(batch_info["schema_id"])
            if not schema_def:
                logger.error(f"❌ Schema not found for batch: {batch_id}")
                return False
            
            # Get collection
            collection = self.mongo_manager.get_collection(schema_def.mongodb_collection_name)
            
            # Delete batch documents
            deleted_count = self.mongo_manager.delete_batch(collection, batch_id)
            
            # Update batch status
            self._update_batch_status(batch_id, "rolled_back", 0)
            
            # Log audit entry
            self._log_audit_entry(
                batch_id=batch_id,
                operation_type="rollback",
                document_id=None,
                original_data=None,
                new_data={"deleted_count": deleted_count},
                row_number=None,
                error_message=None
            )
            
            logger.info(f"✅ Rollback completed: {deleted_count} documents removed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def get_import_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent import history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List[Dict]: Import history records
        """
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ib.batch_id,
                    ib.file_name,
                    sd.schema_name,
                    ib.total_rows,
                    ib.inserted_rows,
                    ib.skipped_rows,
                    ib.error_rows,
                    ib.processing_time_ms,
                    ib.status,
                    ib.created_at
                FROM import_batches ib
                LEFT JOIN schema_definitions sd ON ib.schema_id = sd.schema_id
                ORDER BY ib.created_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            history = []
            
            for row in rows:
                history.append({
                    "batch_id": row["batch_id"],
                    "file_name": row["file_name"],
                    "schema_name": row["schema_name"],
                    "total_rows": row["total_rows"],
                    "inserted_rows": row["inserted_rows"],
                    "skipped_rows": row["skipped_rows"],
                    "error_rows": row["error_rows"],
                    "processing_time_ms": row["processing_time_ms"],
                    "status": row["status"],
                    "created_at": row["created_at"]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to get import history: {e}")
            return []
    
    def _create_import_batch(self, file_info: ExcelFileInfo, schema_def: SchemaDefinition) -> ImportBatch:
        """Create a new import batch record."""
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        
        batch = ImportBatch(
            batch_id=batch_id,
            schema_id=schema_def.schema_id,
            file_name=file_info.file_name,
            file_hash=file_info.file_hash,
            data_start_row=schema_def.data_start_row,
            total_rows=file_info.total_rows,
            created_at=datetime.now()
        )
        
        # Save to database
        self._save_import_batch(batch)
        
        logger.info(f"📦 Created import batch: {batch_id}")
        return batch
    
    def _save_import_batch(self, batch: ImportBatch) -> None:
        """Save import batch to database."""
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO import_batches 
                (batch_id, schema_id, file_name, file_hash, data_start_row, 
                 total_rows, inserted_rows, skipped_rows, error_rows, 
                 processing_time_ms, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                batch.batch_id,
                batch.schema_id,
                batch.file_name,
                batch.file_hash,
                batch.data_start_row,
                batch.total_rows,
                0,  # inserted_rows
                0,  # skipped_rows
                0,  # error_rows
                0,  # processing_time_ms
                batch.status,
                batch.created_at.isoformat()
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to save import batch: {e}")
            raise
    
    def _process_data_chunks(self, file_path: Path, schema_def: SchemaDefinition, 
                           collection, duplicate_strategy: str, file_info: ExcelFileInfo) -> ImportResult:
        """Process Excel data in chunks."""
        total_inserted = 0
        total_modified = 0
        total_skipped = 0
        total_errors = 0
        error_messages = []
        quality_issues: List[Dict[str, Any]] = []
        
        start_time = datetime.now()
        
        try:
            # Read data in chunks
            chunk_count = 0
            for chunk_df in self.excel_processor.read_data_chunked(
                file_path, 
                start_row=schema_def.data_start_row,
                chunk_size=1000
            ):
                chunk_count += 1
                logger.debug(f"📦 Processing chunk {chunk_count}: {len(chunk_df)} rows")
                
                # Transform chunk data
                try:
                    transformed_chunk = self._transform_dataframe(chunk_df, schema_def)
                    documents = transformed_chunk.to_dict('records')
                    
                    # Add batch ID to each document
                    for doc in documents:
                        doc['_batch_id'] = self.current_batch.batch_id if self.current_batch and hasattr(self.current_batch, 'batch_id') else "unknown"
                        doc['_imported_at'] = datetime.now()
                    
                    # Process based on duplicate strategy
                    if duplicate_strategy == "skip":
                        chunk_result = self._process_chunk_with_skip(
                            collection, documents, schema_def.duplicate_detection_columns
                        )
                    elif duplicate_strategy == "upsert":
                        chunk_result = self.mongo_manager.bulk_upsert(
                            collection, documents, schema_def.duplicate_detection_columns
                        )
                    else:  # update strategy
                        chunk_result = self._process_chunk_with_update(
                            collection, documents, schema_def.duplicate_detection_columns
                        )
                    
                    # Update counters
                    total_inserted += chunk_result.inserted_count
                    total_modified += chunk_result.modified_count + chunk_result.upserted_count
                    total_errors += len(chunk_result.errors)
                    
                    if chunk_result.errors:
                        error_messages.extend([str(err) for err in chunk_result.errors])
                    
                    # Update progress
                    processed_rows = total_inserted + total_modified + total_skipped + total_errors
                    self._update_progress(processed_rows, file_info.total_rows, start_time)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process chunk {chunk_count}: {e}")
                    total_errors += len(chunk_df)
                    error_messages.append(f"Chunk {chunk_count}: {str(e)}")
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return ImportResult(
                batch_id=self.current_batch.batch_id if self.current_batch and hasattr(self.current_batch, 'batch_id') else "unknown",
                success=total_errors == 0,
                total_rows=file_info.total_rows,
                inserted_rows=total_inserted,
                modified_rows=total_modified,
                skipped_rows=total_skipped,
                error_rows=total_errors,
                processing_time_ms=processing_time,
                error_messages=error_messages,
                quality_issues=quality_issues
            )
            
        except Exception as e:
            logger.error(f"❌ Data processing failed: {e}")
            raise
    
    def _transform_dataframe(self, df: pd.DataFrame, schema_def: SchemaDefinition) -> pd.DataFrame:
        """Transform DataFrame using schema definition."""
        try:
            # Ensure we have a DataFrame
            if isinstance(df, dict):
                logger.warning(f"⚠️ Received dict instead of DataFrame, converting...")
                df = pd.DataFrame([df])  # Convert dict to DataFrame with single row
            elif isinstance(df, list):
                logger.warning(f"⚠️ Received list instead of DataFrame, converting...")
                df = pd.DataFrame(df)
            elif not isinstance(df, pd.DataFrame):
                logger.warning(f"⚠️ Received {type(df)} instead of DataFrame, converting...")
                df = pd.DataFrame(df)
            
            # Ensure DataFrame is not empty
            if df.empty:
                logger.warning(f"⚠️ Empty DataFrame received, returning empty DataFrame")
                return df
            
            # Ensure DataFrame has proper structure
            if df.columns.empty:
                logger.warning(f"⚠️ DataFrame has no columns, adding default column")
                df = pd.DataFrame(df.values, columns=['Column_0'])
            
            transformed_df = df.copy()
            
            # Map column names based on schema
            if schema_def.normalized_attributes:
                # Create column mapping
                column_mapping = {}
                for excel_col in schema_def.excel_column_names:
                    if excel_col in schema_def.normalized_attributes:
                        normalized_name = schema_def.normalized_attributes[excel_col].field_name
                        column_mapping[excel_col] = normalized_name
                
                # Rename columns (only if they exist in the DataFrame)
                existing_columns = [col for col in column_mapping.keys() if col in transformed_df.columns]
                if existing_columns:
                    rename_dict = {col: column_mapping[col] for col in existing_columns}
                    transformed_df = transformed_df.rename(columns=rename_dict)
                    logger.debug(f"✅ Renamed {len(rename_dict)} columns: {rename_dict}")
                else:
                    logger.warning(f"⚠️ No matching columns found for schema mapping")
            
            # Data type conversions could be added here based on schema
            
            return transformed_df
            
        except Exception as e:
            logger.error(f"❌ Data transformation failed: {e}")
            raise
    
    def _process_chunk_with_skip(self, collection, documents: List[Dict], 
                               duplicate_fields: List[str]) -> BulkOperationResult:
        """Process chunk with skip duplicate strategy."""
        non_duplicate_docs = []
        skipped_count = 0
        
        for doc in documents:
            duplicate_result = self.mongo_manager.check_duplicates(
                collection, doc, duplicate_fields
            )
            
            if not duplicate_result.is_duplicate:
                non_duplicate_docs.append(doc)
            else:
                skipped_count += 1
        
        if non_duplicate_docs:
            result = self.mongo_manager.bulk_insert(collection, non_duplicate_docs)
            # Add skipped count to result
            result.inserted_count = len(non_duplicate_docs) - len(result.errors)
            return result
        else:
            return BulkOperationResult(0, 0, 0, 0, [], 0)
    
    def _process_chunk_with_update(self, collection, documents: List[Dict], 
                                 duplicate_fields: List[str]) -> BulkOperationResult:
        """Process chunk with update duplicate strategy."""
        # For now, implement as upsert - could be enhanced for true update logic
        return self.mongo_manager.bulk_upsert(collection, documents, duplicate_fields)
    
    def _update_progress(self, processed_rows: int, total_rows: int, start_time: datetime) -> None:
        """Update and broadcast progress information."""
        if not self.progress_callback:
            return
        
        current_time = datetime.now()
        elapsed_ms = int((current_time - start_time).total_seconds() * 1000)
        
        progress_percentage = (processed_rows / total_rows) * 100 if total_rows > 0 else 0
        
        # Estimate remaining time
        if processed_rows > 0:
            avg_time_per_row = elapsed_ms / processed_rows
            remaining_rows = total_rows - processed_rows
            estimated_remaining_ms = int(avg_time_per_row * remaining_rows)
        else:
            estimated_remaining_ms = 0
        
        progress = ImportProgress(
            batch_id=self.current_batch.batch_id if self.current_batch and hasattr(self.current_batch, 'batch_id') else "unknown",
            total_rows=total_rows,
            processed_rows=processed_rows,
            inserted_rows=0,  # Updated by caller
            skipped_rows=0,   # Updated by caller
            error_rows=0,     # Updated by caller
            current_operation="Processing data",
            processing_time_ms=elapsed_ms,
            estimated_remaining_ms=estimated_remaining_ms,
            progress_percentage=progress_percentage
        )
        
        self.progress_callback(progress)
    
    def _update_batch_status(self, batch_id: str, status: str, processing_time_ms: int) -> None:
        """Update batch status in database."""
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE import_batches 
                SET status = ?, processing_time_ms = ?
                WHERE batch_id = ?
            """, (status, processing_time_ms, batch_id))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to update batch status: {e}")
    
    def _get_batch_info(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch information from database."""
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM import_batches WHERE batch_id = ?
            """, (batch_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get batch info: {e}")
            return None
    
    def _log_audit_entry(self, batch_id: str, operation_type: str, document_id: Optional[str],
                        original_data: Optional[Dict], new_data: Optional[Dict],
                        row_number: Optional[int], error_message: Optional[str]) -> None:
        """Log audit entry for tracking changes."""
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_log 
                (batch_id, operation_type, document_id, original_data, new_data,
                 row_number, timestamp, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                batch_id,
                operation_type,
                document_id,
                str(original_data) if original_data else None,
                str(new_data) if new_data else None,
                row_number,
                datetime.now().isoformat(),
                error_message
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to log audit entry: {e}")