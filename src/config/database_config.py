"""
Database Configuration and Connection Management

This module handles database connections, schema creation, and connection pooling
for both SQLite and MongoDB databases.
"""

import sqlite3
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from config.settings import get_settings
from config.paths import get_database_path


class SQLiteManager:
    """Manages SQLite database connections and schema."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_path = get_database_path()
        self._connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get SQLite database connection.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._connection.row_factory = sqlite3.Row  # Enable dict-like access
            self._setup_database()
        
        return self._connection
    
    def _setup_database(self) -> None:
        """Setup database schema if it doesn't exist."""
        conn = self._connection
        if not conn:
            raise RuntimeError("Database connection not initialized")
        cursor = conn.cursor()
        
        # Create schema_definitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_definitions (
                schema_id TEXT PRIMARY KEY,
                schema_name TEXT UNIQUE NOT NULL,
                original_columns TEXT, -- JSON array of user-pasted column names
                normalized_attributes TEXT, -- JSON object mapping original -> normalized
                suggested_indexes TEXT, -- JSON array of index definitions
                duplicate_detection_columns TEXT, -- JSON array of column names
                duplicate_strategy TEXT DEFAULT 'skip', -- skip, update, upsert
                data_start_row INTEGER DEFAULT 2, -- Default data start row
                mongodb_collection_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        """)
        
        # Create import_batches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_batches (
                batch_id TEXT PRIMARY KEY,
                schema_id TEXT REFERENCES schema_definitions(schema_id),
                file_name TEXT,
                file_hash TEXT, -- To identify duplicate files
                data_start_row INTEGER,
                total_rows INTEGER,
                inserted_rows INTEGER,
                skipped_rows INTEGER,
                error_rows INTEGER,
                processing_time_ms INTEGER,
                status TEXT DEFAULT 'in_progress', -- in_progress, completed, failed, rolled_back
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create audit_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT REFERENCES import_batches(batch_id),
                operation_type TEXT, -- insert, update, skip, delete, rollback
                document_id TEXT, -- MongoDB document _id
                original_data TEXT, -- JSON of original document (for rollback)
                new_data TEXT, -- JSON of new/updated document
                row_number INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        """)
        
        # Create data_quality_issues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_quality_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT REFERENCES import_batches(batch_id),
                issue_type TEXT, -- validation_error, type_mismatch, missing_required, duplicate_found
                row_number INTEGER,
                column_name TEXT,
                original_value TEXT,
                expected_type TEXT,
                severity TEXT, -- error, warning, info
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create UI state and user preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                last_used_schema_id TEXT REFERENCES schema_definitions(schema_id),
                last_import_directory TEXT,
                default_data_start_row INTEGER DEFAULT 2,
                default_duplicate_strategy TEXT DEFAULT 'skip',
                ui_theme TEXT DEFAULT 'light',
                window_size TEXT, -- JSON: {"width": 1200, "height": 800}
                recent_files TEXT, -- JSON array of recent file paths
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create file processing history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_processing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                file_size INTEGER,
                last_processed_at DATETIME,
                schema_id TEXT REFERENCES schema_definitions(schema_id),
                total_processing_time_ms INTEGER,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create schema usage analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schema_id TEXT REFERENCES schema_definitions(schema_id),
                usage_date DATE,
                files_processed INTEGER DEFAULT 0,
                total_rows_processed INTEGER DEFAULT 0,
                average_processing_time_ms INTEGER,
                error_rate FLOAT DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_schema_fingerprint ON schema_definitions(schema_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_used ON schema_definitions(last_used DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_batch_schema ON import_batches(schema_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_batch ON audit_log(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_batch ON data_quality_issues(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ui_user ON ui_state(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON file_processing_history(file_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_schema_analytics ON schema_analytics(schema_id, usage_date)")
        
        if conn:
            conn.commit()
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None


class MongoManager:
    """Manages MongoDB connections and collections."""
    
    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
    
    def get_client(self) -> MongoClient:
        """
        Get MongoDB client connection.
        
        Returns:
            MongoClient: MongoDB client
        """
        if self._client is None:
            if not self.settings.database.mongo_url:
                raise ValueError("MongoDB URL not configured. Set MONGO_URL environment variable.")
            
            self._client = MongoClient(
                self.settings.database.mongo_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                maxPoolSize=10,
                retryWrites=True
            )
            
            # Test connection
            self._client.admin.command('ping')
        
        return self._client
    
    def get_database(self) -> Database:
        """
        Get MongoDB database.
        
        Returns:
            Database: MongoDB database instance
        """
        if self._database is None:
            client = self.get_client()
            self._database = client[self.settings.database.mongo_database]
        
        return self._database
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        Get MongoDB collection for Excel file data.
        
        Args:
            collection_name: Name of the collection (usually Excel file identifier)
            
        Returns:
            Collection: MongoDB collection instance
        """
        database = self.get_database()
        return database[collection_name]
    
    def create_excel_collection(self, excel_file_id: str) -> Collection:
        """
        Create a new collection for an Excel file.
        
        Args:
            excel_file_id: Unique identifier for the Excel file
            
        Returns:
            Collection: New MongoDB collection
        """
        database = self.get_database()
        collection_name = f"excel_{excel_file_id}"
        return database[collection_name]
    
    def get_excel_collections(self) -> list:
        """
        Get all Excel file collections.
        
        Returns:
            list: List of collection names
        """
        database = self.get_database()
        return [name for name in database.list_collection_names() if name.startswith('excel_')]
    
    def test_connection(self) -> bool:
        """
        Test MongoDB connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            client = self.get_client()
            client.admin.command('ping')
            return True
        except Exception as e:
            print(f"MongoDB connection test failed: {e}")
            return False
    
    def close(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None


class DatabaseManager:
    """Manages both SQLite and MongoDB connections."""
    
    def __init__(self):
        self.sqlite = SQLiteManager()
        self.mongo = MongoManager()
    
    def initialize(self) -> bool:
        """
        Initialize both database connections.
        
        Returns:
            bool: True if both connections successful, False otherwise
        """
        try:
            # Initialize SQLite (always succeeds or throws)
            self.sqlite.get_connection()
            print("✓ SQLite database initialized")
            
            # Test MongoDB connection
            if self.mongo.test_connection():
                print("✓ MongoDB connection successful")
                return True
            else:
                print("✗ MongoDB connection failed")
                return False
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            return False
    
    def close_all(self) -> None:
        """Close all database connections."""
        self.sqlite.close()
        self.mongo.close()


# Global database manager instance
db_manager = DatabaseManager()


def get_sqlite_connection() -> sqlite3.Connection:
    """
    Get SQLite database connection.
    
    Returns:
        sqlite3.Connection: SQLite connection
    """
    return db_manager.sqlite.get_connection()


def get_mongo_database() -> Database:
    """
    Get MongoDB database.
    
    Returns:
        Database: MongoDB database instance
    """
    return db_manager.mongo.get_database()


def get_mongo_collection(collection_name: str) -> Collection:
    """
    Get MongoDB collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection: MongoDB collection instance
    """
    return db_manager.mongo.get_collection(collection_name)
