# Data Ingestion App - Method Signatures

## Schema Management Module

### SchemaManager Class

```python
def get_all_schemas() -> List[SchemaDefinition]:
    """
    Retrieve all schema definitions from SQL database.
    
    Returns:
        List of all available schema definitions ordered by last_used DESC
    """

def create_schema(schema_name: str, column_names: List[str]) -> str:
    """
    Generate unique schema_id and initiate AI processing workflow.
    
    Args:
        schema_name: User-provided name for the schema
        column_names: List of column names pasted from Excel
        
    Returns:
        Generated schema_id for tracking the creation process
    """

def save_schema_definition(schema_data: SchemaDefinition) -> bool:
    """
    Save AI-processed schema definition to SQL database.
    
    Args:
        schema_data: Complete schema definition with AI suggestions
        
    Returns:
        True if saved successfully, False otherwise
    """

def get_schema_by_id(schema_id: str) -> Optional[SchemaDefinition]:
    """
    Retrieve specific schema definition by ID.
    
    Args:
        schema_id: Unique identifier for the schema
        
    Returns:
        Schema definition if found, None otherwise
    """

def update_schema_usage(schema_id: str) -> None:
    """
    Increment usage count and update last_used timestamp.
    
    Args:
        schema_id: Schema that was used for import
    """

def update_schema_data_start_row(schema_id: str, start_row: int) -> bool:
    """
    Update the default data start row for a schema.
    
    Args:
        schema_id: Schema to update
        start_row: New default start row (1-10)
        
    Returns:
        True if updated successfully
    """

def delete_schema(schema_id: str) -> bool:
    """
    Delete schema definition and associated data.
    
    Args:
        schema_id: Schema to delete
        
    Returns:
        True if deleted successfully
    """
```

## AI Integration Module

### AISchemaProcessor Class

```python
def process_columns(column_names: List[str]) -> AISchemaResponse:
    """
    Send column names to OpenAI API and parse the response.
    
    Args:
        column_names: Raw column names from Excel header
        
    Returns:
        Structured AI response with normalized attributes and suggestions
        
    Raises:
        AIProcessingError: If API call fails or response is invalid
    """

def validate_ai_response(response: dict) -> bool:
    """
    Validate AI response structure and content integrity.
    
    Args:
        response: Raw response from OpenAI API
        
    Returns:
        True if response is valid and usable
    """

def generate_system_prompt() -> str:
    """
    Generate the system prompt for OpenAI API calls.
    
    Returns:
        Formatted system prompt string
    """

def generate_user_prompt(columns: List[str]) -> str:
    """
    Generate user prompt with column data for AI processing.
    
    Args:
        columns: List of column names to process
        
    Returns:
        Formatted user prompt string
    """

def retry_ai_request(columns: List[str], max_retries: int = 3) -> AISchemaResponse:
    """
    Retry AI processing with exponential backoff on failure.
    
    Args:
        columns: Column names to process
        max_retries: Maximum number of retry attempts
        
    Returns:
        AI response or raises exception after max retries
    """
```

## MongoDB Integration Module

### MongoCollectionManager Class

```python
def create_collection(collection_name: str, schema_def: SchemaDefinition) -> bool:
    """
    Create MongoDB collection with proper schema validation.
    
    Args:
        collection_name: Name for the new collection
        schema_def: Schema definition with field specifications
        
    Returns:
        True if collection created successfully
    """

def create_indexes(collection_name: str, index_definitions: List[IndexDefinition]) -> bool:
    """
    Create suggested indexes on collection for optimal performance.
    
    Args:
        collection_name: Target collection name
        index_definitions: List of index specifications from AI
        
    Returns:
        True if all indexes created successfully
    """

def check_document_exists(collection_name: str, raw_row_data: dict, schema_def: SchemaDefinition) -> Optional[dict]:
    """
    Check if document exists based on duplicate detection logic using mapped field names.
    
    Args:
        collection_name: Target collection
        raw_row_data: Raw Excel row data with original column names
        schema_def: Schema definition with column mappings
        
    Returns:
        Existing document if found, None otherwise
    """

def bulk_insert_documents(collection_name: str, documents: List[dict]) -> BulkInsertResult:
    """
    Perform bulk insert operation with duplicate checking.
    
    Args:
        collection_name: Target collection
        documents: List of normalized documents to insert
        
    Returns:
        Result object with inserted/skipped counts and errors
    """

def insert_document_with_metadata(collection_name: str, document: dict, batch_id: str, row_number: int) -> Optional[str]:
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

def update_document(collection_name: str, filter_keys: dict, document: dict, batch_id: str) -> bool:
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

def rollback_batch(collection_name: str, batch_id: str) -> RollbackResult:
    """
    Remove all documents from a specific import batch.
    
    Args:
        collection_name: Target collection
        batch_id: Batch to rollback
        
    Returns:
        Result object with rollback statistics
    """

def get_collection_stats(collection_name: str) -> CollectionStats:
    """
    Get collection statistics for monitoring.
    
    Returns:
        Statistics object with document counts, indexes, etc.
    """
```

## Excel Processing Module

### ExcelProcessor Class

```python
def read_excel_file_stream(file_path: str, start_row: int, batch_size: int = 1000) -> Iterator[List[dict]]:
    """
    Stream Excel file in batches to manage memory efficiently.
    
    Args:
        file_path: Path to Excel file
        start_row: Row number to start reading data (1-based)
        batch_size: Number of rows to read per batch
        
    Yields:
        Batches of row data as dictionaries with original Excel column names
    """

def validate_excel_structure(file_path: str, expected_columns: List[str], header_row: int = 1) -> ValidationResult:
    """
    Validate Excel file structure matches expected schema.
    
    Args:
        file_path: Path to Excel file
        expected_columns: Expected column names from schema (original Excel names)
        header_row: Row containing column headers
        
    Returns:
        Validation result with success/failure and details
    """

def preview_excel_data(file_path: str, start_row: int, limit: int = 5) -> List[dict]:
    """
    Preview first few rows of Excel data for user verification.
    
    Args:
        file_path: Path to Excel file
        start_row: Row to start preview from
        limit: Maximum number of rows to preview
        
    Returns:
        List of row data dictionaries with original Excel column names
    """

def get_excel_column_names(file_path: str, header_row: int = 1) -> List[str]:
    """
    Extract column names from Excel file header row.
    
    Args:
        file_path: Path to Excel file
        header_row: Row number containing headers (1-based)
        
    Returns:
        List of column names as they appear in Excel
    """

def get_excel_row_count(file_path: str) -> int:
    """
    Get total number of rows in Excel file efficiently.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        Total row count including headers
    """

def calculate_file_hash(file_path: str) -> str:
    """
    Calculate hash of Excel file for duplicate detection.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        SHA-256 hash of file content
    """
```

## Data Ingestion Module

### DataIngestionEngine Class

```python
def process_excel_file_async(schema_id: str, file_path: str, start_row: int) -> IngestionResult:
    """
    Main asynchronous method to process entire Excel file with progress tracking.
    
    Args:
        schema_id: Schema definition to use
        file_path: Path to Excel file
        start_row: Row number to start data processing
        
    Returns:
        Complete ingestion result with statistics
    """

def process_batch_async(batch_data: List[dict], schema_def: SchemaDefinition, batch_id: str) -> BatchProcessingResult:
    """
    Process a batch of rows asynchronously with duplicate checking.
    
    Args:
        batch_data: List of raw Excel row data dictionaries
        schema_def: Schema definition for processing
        batch_id: Import batch identifier
        
    Returns:
        Batch processing result with per-row outcomes
    """

def normalize_row_data(raw_data: dict, schema_def: SchemaDefinition) -> dict:
    """
    Transform raw Excel data to normalized MongoDB document format.
    
    Args:
        raw_data: Raw row data from Excel with original column names
        schema_def: Schema with normalization rules and column mappings
        
    Returns:
        Normalized document ready for MongoDB insertion with mapped field names
    """

def validate_row_data(normalized_data: dict, schema_def: SchemaDefinition) -> ValidationResult:
    """
    Validate normalized row data against schema requirements.
    
    Args:
        normalized_data: Normalized document data with MongoDB field names
        schema_def: Schema with validation rules
        
    Returns:
        Validation result with errors/warnings
    """

def handle_duplicate_document(existing_doc: dict, new_doc: dict, strategy: str, batch_id: str) -> DuplicateHandlingResult:
    """
    Handle duplicate document based on configured strategy.
    
    Args:
        existing_doc: Document already in database
        new_doc: New document being processed
        strategy: 'skip', 'update', or 'upsert'
        batch_id: Current import batch ID
        
    Returns:
        Result indicating action taken
    """

def create_import_batch(schema_id: str, file_path: str, start_row: int) -> str:
    """
    Create new import batch record for tracking and rollback.
    
    Args:
        schema_id: Schema being used
        file_path: Source Excel file path
        start_row: Data start row
        
    Returns:
        Generated batch_id
    """

def finalize_import_batch(batch_id: str, result: IngestionResult) -> bool:
    """
    Update import batch record with final results.
    
    Args:
        batch_id: Batch to finalize
        result: Complete ingestion results
        
    Returns:
        True if finalized successfully
    """
```

## Column Mapping Module

### ColumnMappingManager Class

```python
def find_excel_column_for_mongodb_field(mongodb_field: str, schema_def: SchemaDefinition) -> Optional[str]:
    """
    Reverse lookup: find Excel column name that maps to a MongoDB field.
    
    Args:
        mongodb_field: MongoDB field name (e.g., "customer_email")
        schema_def: Schema definition with mappings
        
    Returns:
        Excel column name (e.g., "Customer Email") or None if not found
    """

def convert_value_to_type(value: Any, target_type: str) -> Any:
    """
    Convert Excel cell value to the target MongoDB data type.
    
    Args:
        value: Raw value from Excel cell
        target_type: Target type ("String", "Number", "Date", "Boolean")
        
    Returns:
        Converted value in correct type
        
    Raises:
        DataConversionError: If conversion fails
    """

def validate_column_mapping(excel_columns: List[str], schema_def: SchemaDefinition) -> MappingValidationResult:
    """
    Validate that Excel file columns can be properly mapped to schema.
    
    Args:
        excel_columns: Column names from Excel file
        schema_def: Schema definition to validate against
        
    Returns:
        Validation result with mapping success/issues
    """

def handle_column_mapping_issues(raw_data: dict, schema_def: SchemaDefinition) -> MappingResult:
    """
    Handle various mapping edge cases like unmapped columns and fuzzy matching.
    
    Args:
        raw_data: Raw Excel row data
        schema_def: Schema definition with expected mappings
        
    Returns:
        Mapping result with normalized data and any issues found
    """

def find_closest_column_name(target_column: str, available_columns: List[str]) -> Optional[str]:
    """
    Find the closest matching column name using fuzzy string matching.
    
    Args:
        target_column: Column name we're looking for
        available_columns: Available column names to match against
        
    Returns:
        Best matching column name or None if no good match
    """

def similarity_score(str1: str, str2: str) -> float:
    """
    Calculate similarity score between two strings (0.0 to 1.0).
    
    Args:
        str1: First string to compare
        str2: Second string to compare
        
    Returns:
        Similarity score where 1.0 is exact match
    """

def get_field_data_type(mongodb_field: str, schema_def: SchemaDefinition) -> str:
    """
    Get the expected data type for a MongoDB field from schema definition.
    
    Args:
        mongodb_field: MongoDB field name
        schema_def: Schema definition
        
    Returns:
        Data type string ("String", "Number", "Date", "Boolean")
    """
```

## Audit & Quality Module

### AuditLogger Class

```python
def log_document_operation(batch_id: str, operation: str, document_id: str, original_data: dict, new_data: dict, row_number: int) -> None:
    """
    Log document operation for audit trail and rollback capability.
    
    Args:
        batch_id: Import batch identifier
        operation: Type of operation (insert, update, skip, delete)
        document_id: MongoDB document _id
        original_data: Original document state (for updates)
        new_data: New document state
        row_number: Excel row number
    """

def log_data_quality_issue(batch_id: str, issue_type: str, row_number: int, column_name: str, issue_details: dict) -> None:
    """
    Log data quality issue for reporting and analysis.
    
    Args:
        batch_id: Import batch identifier
        issue_type: Type of quality issue
        row_number: Excel row with issue
        column_name: Column containing issue (original Excel name)
        issue_details: Detailed issue information
    """

def get_batch_audit_trail(batch_id: str) -> List[AuditLogEntry]:
    """
    Retrieve complete audit trail for an import batch.
    
    Args:
        batch_id: Batch to retrieve audit trail for
        
    Returns:
        List of audit log entries chronologically ordered
    """

def get_data_quality_report(batch_id: str) -> DataQualityReport:
    """
    Generate data quality report for an import batch.
    
    Args:
        batch_id: Batch to generate report for
        
    Returns:
        Comprehensive data quality report
    """
```

### RollbackManager Class

```python
def rollback_import_batch(batch_id: str) -> RollbackResult:
    """
    Rollback complete import batch with full audit trail.
    
    Args:
        batch_id: Batch to rollback
        
    Returns:
        Rollback result with statistics and success status
    """

def can_rollback_batch(batch_id: str) -> bool:
    """
    Check if batch can be safely rolled back.
    
    Args:
        batch_id: Batch to check
        
    Returns:
        True if rollback is possible
    """

def get_rollback_preview(batch_id: str) -> RollbackPreview:
    """
    Preview what would be affected by rollback operation.
    
    Args:
        batch_id: Batch to preview rollback for
        
    Returns:
        Preview of documents and operations that would be reversed
    """

def restore_document_state(document_id: str, original_state: dict) -> bool:
    """
    Restore document to its original state before import.
    
    Args:
        document_id: MongoDB document _id
        original_state: Original document data
        
    Returns:
        True if restored successfully
    """
```

## Batch Processing Module

### BatchImportManager Class

```python
def process_multiple_files(schema_id: str, file_paths: List[str], start_row: int) -> MultiBatchResult:
    """
    Process multiple Excel files in parallel batches.
    
    Args:
        schema_id: Schema to use for all files
        file_paths: List of Excel file paths
        start_row: Data start row for all files
        
    Returns:
        Combined results from all file processing
    """

def get_import_history(schema_id: str, limit: int = 50) -> List[ImportBatchSummary]:
    """
    Get import history for a specific schema.
    
    Args:
        schema_id: Schema to get history for
        limit: Maximum number of batches to return
        
    Returns:
        List of import batch summaries ordered by date
    """

def get_batch_details(batch_id: str) -> ImportBatchDetails:
    """
    Get detailed information about a specific import batch.
    
    Args:
        batch_id: Batch to get details for
        
    Returns:
        Detailed batch information including statistics and errors
    """

def delete_old_batches(days_old: int = 30) -> int:
    """
    Clean up old import batches and associated audit logs.
    
    Args:
        days_old: Delete batches older than this many days
        
    Returns:
        Number of batches deleted
    """
```

## UI Controllers Module

### MainWindowController Class

```python
def initialize_app() -> None:
    """
    Initialize application, populate schema dropdown, and check database connections.
    """

def on_schema_selected(schema_id: str) -> None:
    """
    Handle schema selection and update UI with schema defaults.
    
    Args:
        schema_id: Selected schema identifier
    """

def on_data_start_row_changed(new_row: int) -> None:
    """
    Handle data start row change and update preview if file is loaded.
    
    Args:
        new_row: New start row value (1-10)
    """

def on_file_selected(file_path: str) -> None:
    """
    Handle Excel file selection and validate against current schema.
    
    Args:
        file_path: Path to selected Excel file
    """

def on_preview_data_clicked() -> None:
    """
    Show preview of Excel data using current schema and start row settings.
    """

def on_start_import_clicked() -> None:
    """
    Begin asynchronous data import process with progress tracking.
    """

def update_import_progress(current: int, total: int, message: str) -> None:
    """
    Update progress bar and status message during import.
    
    Args:
        current: Current row being processed
        total: Total rows to process
        message: Status message to display
    """

def on_view_history_clicked() -> None:
    """
    Show import history and rollback management window.
    """

def handle_import_completion(result: IngestionResult) -> None:
    """
    Handle import completion and show results to user.
    
    Args:
        result: Complete import results
    """
```

### SchemaCreationController Class

```python
def on_new_schema_clicked() -> None:
    """
    Show schema creation modal with empty form.
    """

def on_generate_schema_clicked(schema_name: str, columns: str, default_start_row: int) -> None:
    """
    Process schema creation request with AI assistance.
    
    Args:
        schema_name: User-provided schema name
        columns: Raw column names from Excel (original names)
        default_start_row: Default data start row for this schema
    """

def show_ai_processing_progress() -> None:
    """
    Show progress indicator while AI processes schema.
    """

def show_ai_results(ai_response: AISchemaResponse) -> None:
    """
    Display AI processing results for user review and modification.
    
    Args:
        ai_response: Structured response from AI processing
    """

def on_modify_schema_clicked(current_schema: SchemaDefinition) -> None:
    """
    Allow user to modify AI-generated schema before saving.
    
    Args:
        current_schema: Current schema definition to modify
    """

def on_create_schema_confirmed(schema_data: SchemaDefinition) -> None:
    """
    Finalize schema creation and update main window.
    
    Args:
        schema_data: Final schema definition to save
    """

def handle_schema_creation_error(error: Exception) -> None:
    """
    Handle and display schema creation errors to user.
    
    Args:
        error: Exception that occurred during creation
    """
```

### HistoryController Class

```python
def show_import_history(schema_id: str) -> None:
    """
    Display import history window for current schema.
    
    Args:
        schema_id: Schema to show history for
    """

def on_rollback_batch_clicked(batch_id: str) -> None:
    """
    Handle rollback request with confirmation dialog.
    
    Args:
        batch_id: Batch to rollback
    """

def show_rollback_confirmation(batch_id: str, preview: RollbackPreview) -> None:
    """
    Show rollback confirmation dialog with impact preview.
    
    Args:
        batch_id: Batch to rollback
        preview: Preview of rollback impact
    """

def execute_rollback(batch_id: str) -> None:
    """
    Execute rollback operation with progress tracking.
    
    Args:
        batch_id: Batch to rollback
    """

def on_view_batch_details(batch_id: str) -> None:
    """
    Show detailed view of import batch results.
    
    Args:
        batch_id: Batch to show details for
    """

def show_data_quality_report(batch_id: str) -> None:
    """
    Display data quality report for import batch.
    
    Args:
        batch_id: Batch to show quality report for
    """
```

## Data Models

### Core Data Classes

```python
@dataclass
class SchemaDefinition:
    """
    Complete schema definition with column mappings and metadata.
    """
    schema_id: str
    schema_name: str
    original_columns: List[str]  # Original Excel column names
    normalized_attributes: Dict[str, AttributeDefinition]  # Excel name -> MongoDB mapping
    suggested_indexes: List[IndexDefinition]
    duplicate_detection_columns: List[str]  # MongoDB field names for duplicate detection
    duplicate_strategy: str  # 'skip', 'update', 'upsert'
    data_start_row: int  # Default data start row for this schema
    mongodb_collection_name: str
    created_at: datetime
    last_used: datetime
    usage_count: int

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
    field: str  # MongoDB field name
    type: str  # unique, ascending, descending, text
    reason: str

@dataclass
class AISchemaResponse:
    """
    Structured response from AI schema processing.
    """
    normalized_attributes: Dict[str, AttributeDefinition]
    suggested_indexes: List[IndexDefinition]
    duplicate_detection: Dict[str, Any]
    collection_name: str

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
class ValidationResult:
    """
    Result of data validation operations.
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]

@dataclass
class MappingValidationResult:
    """
    Result of column mapping validation.
    """
    is_valid: bool
    mapped_columns: Dict[str, str]  # Excel name -> MongoDB name
    unmapped_excel_columns: List[str]
    missing_schema_columns: List[str]
    suggested_mappings: Dict[str, str]  # Fuzzy matches

@dataclass
class MappingResult:
    """
    Result of column mapping operation with issues.
    """
    normalized_data: dict
    issues: List[str]
    mapping_confidence: float

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
class DataQualityReport:
    """
    Data quality analysis report.
    """
    batch_id: str
    total_issues: int
    issues_by_type: Dict[str, int]
    issues_by_severity: Dict[str, int]
    detailed_issues: List[DataQualityIssue]

@dataclass
class DataQualityIssue:
    """
    Individual data quality issue.
    """
    row_number: int
    column_name: str  # Original Excel column name
    issue_type: str
    severity: str
    description: str
    original_value: str
    suggested_fix: Optional[str]
```
