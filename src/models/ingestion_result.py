"""
Data models for ingestion results and MongoDB operations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class IngestionResult:
    """
    Complete results from data ingestion process.
    """
    total_rows: int
    inserted_rows: int
    skipped_rows: int
    error_rows: int
    processing_time_ms: int
    errors: List[str]


@dataclass
class BatchProcessingResult:
    """
    Result from processing a batch of rows.
    """
    processed_count: int
    inserted_count: int
    skipped_count: int
    error_count: int
    errors: List[str]


@dataclass
class BulkInsertResult:
    """
    Result from MongoDB bulk insert operation.
    """
    inserted_count: int
    skipped_count: int
    error_count: int
    errors: List[str]
    inserted_ids: List[str]


@dataclass
class RollbackResult:
    """
    Result of rollback operation.
    """
    success: bool
    documents_deleted: int
    documents_restored: int
    errors: List[str]
    processing_time_ms: int


@dataclass
class CollectionStats:
    """
    MongoDB collection statistics.
    """
    document_count: int
    index_count: int
    size_bytes: int
    average_object_size: float
    indexes: List[Dict[str, Any]]


@dataclass
class DuplicateHandlingResult:
    """
    Result of duplicate document handling.
    """
    action_taken: str  # 'inserted', 'skipped', 'updated'
    document_id: Optional[str]
    message: str


@dataclass
class ProcessingResult:
    """
    Result from processing a single row.
    """
    success: bool
    action: str  # 'inserted', 'skipped', 'updated', 'error'
    document_id: Optional[str]
    error_message: Optional[str]
    row_number: int


@dataclass
class ActionResult:
    """
    Generic result from an action.
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None



