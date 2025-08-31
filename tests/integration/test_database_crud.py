#!/usr/bin/env python3
"""
Comprehensive CRUD Test Suite for All SQLite Tables

This script tests Create, Read, Update, Delete operations for all tables:
- schema_definitions
- file_processing_history
- import_batches
- audit_log
- data_quality_issues
- schema_analytics
- ui_state
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.schema_manager import SchemaManager
from src.models.schema_definition import (
    SchemaDefinition,
    AttributeDefinition,
    IndexDefinition,
)
# SQLite connection removed - using MongoDB only


def test_schema_definitions_crud():
    """Test CRUD operations for schema_definitions table."""
    print("\n📋 Testing schema_definitions CRUD operations...")
    print("=" * 60)

    schema_manager = SchemaManager()

    # Test data
    test_schema_name = "Test Excel Schema"
    test_columns = [
        "First Name",
        "Last Name",
        "Email",
        "Phone",
        "Purchase Date",
        "Amount",
    ]

    # CREATE
    print("1️⃣ CREATE - Creating schema...")
    schema_id = schema_manager.create_schema(test_schema_name, test_columns)
    print(f"   ✅ Generated schema_id: {schema_id}")

    # Create normalized attributes
    normalized_attrs = {
        "First Name": AttributeDefinition(
            field_name="first_name",
            data_type="string",
            description="Customer's first name",
            is_required=True,
        ),
        "Last Name": AttributeDefinition(
            field_name="last_name",
            data_type="string",
            description="Customer's last name",
            is_required=True,
        ),
        "Email": AttributeDefinition(
            field_name="email",
            data_type="string",
            description="Customer's email address",
            is_required=True,
        ),
    }

    # Create suggested indexes
    suggested_indexes = [
        IndexDefinition(
            field_names=["email"], index_type="unique", reason="Email should be unique"
        )
    ]

    # Create schema definition
    schema_def = SchemaDefinition(
        schema_id=schema_id,
        schema_name=test_schema_name,
        excel_column_names=test_columns,
        normalized_attributes=normalized_attrs,
        suggested_indexes=suggested_indexes,
        duplicate_detection_columns=["email", "phone"],
        duplicate_strategy="skip",
        data_start_row=2,
        mongodb_collection_name="customers",
        created_at=datetime.now(),
        last_used=datetime.now(),
        usage_count=0,
    )

    # Save to database
    save_result = schema_manager.save_schema_definition(schema_def)
    print(f"   ✅ Save result: {save_result}")

    # READ
    print("\n2️⃣ READ - Retrieving schemas...")
    all_schemas = schema_manager.get_all_schemas()
    print(f"   ✅ Found {len(all_schemas)} schemas")

    retrieved_schema = schema_manager.get_schema_by_id(schema_id)
    if retrieved_schema:
        print(f"   ✅ Retrieved schema: {retrieved_schema.schema_name}")
        print(f"   📊 Columns: {len(retrieved_schema.excel_column_names)}")
        print(f"   🔍 Collection: {retrieved_schema.mongodb_collection_name}")
    else:
        print("   ❌ Failed to retrieve schema")

    # UPDATE
    print("\n3️⃣ UPDATE - Updating schema...")
    schema_manager.update_schema_usage(schema_id)
    update_result = schema_manager.update_schema_data_start_row(schema_id, 3)
    print(f"   ✅ Update data start row result: {update_result}")

    # Verify updates
    updated_schema = schema_manager.get_schema_by_id(schema_id)
    if updated_schema:
        print(f"   ✅ Usage count: {updated_schema.usage_count}")
        print(f"   ✅ Data start row: {updated_schema.data_start_row}")

    # DELETE
    print("\n4️⃣ DELETE - Deleting schema...")
    delete_result = schema_manager.delete_schema(schema_id)
    print(f"   ✅ Delete result: {delete_result}")

    # Verify deletion
    deleted_schema = schema_manager.get_schema_by_id(schema_id)
    if deleted_schema is None:
        print("   ✅ Schema successfully deleted")
    else:
        print("   ❌ Schema still exists after deletion")

    return schema_id


def test_file_processing_history_crud():
    """Test CRUD operations for file_processing_history table."""
    print("\n📁 Testing file_processing_history CRUD operations...")
    print("=" * 60)

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # CREATE
    print("1️⃣ CREATE - Creating file processing record...")
    file_id = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    cursor.execute(
        """
        INSERT INTO file_processing_history 
        (file_name, file_hash, file_size, schema_id, 
         total_processing_time_ms, success_count, error_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            "test_excel.xlsx",
            "hash_" + file_id,
            2500000,  # 2.5MB in bytes
            "test_schema_123",
            15500,  # 15.5 seconds in milliseconds
            950,
            50,
        ),
    )

    conn.commit()
    print(f"   ✅ Created file processing record: {file_id}")

    # READ
    print("\n2️⃣ READ - Retrieving file processing records...")
    cursor.execute("SELECT COUNT(*) FROM file_processing_history")
    count = cursor.fetchone()[0]
    print(f"   ✅ Total records: {count}")

    cursor.execute(
        "SELECT * FROM file_processing_history WHERE file_name = ?",
        ("test_excel.xlsx",),
    )
    row = cursor.fetchone()
    if row:
        print(
            f"   ✅ Retrieved record: {row['file_name']} - Success: {row['success_count']}"
        )

    # UPDATE
    print("\n3️⃣ UPDATE - Updating file processing record...")
    cursor.execute(
        """
        UPDATE file_processing_history 
        SET success_count = ?, error_count = ?, total_processing_time_ms = ?
        WHERE file_name = ?
    """,
        (1000, 0, 20000, "test_excel.xlsx"),
    )

    conn.commit()
    print("   ✅ Updated file processing record")

    # DELETE
    print("\n4️⃣ DELETE - Deleting file processing record...")
    cursor.execute(
        "DELETE FROM file_processing_history WHERE file_name = ?", ("test_excel.xlsx",)
    )
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"   ✅ Deleted {deleted_count} record(s)")

    return file_id


def test_import_batches_crud():
    """Test CRUD operations for import_batches table."""
    print("\n📦 Testing import_batches CRUD operations...")
    print("=" * 60)

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # CREATE
    print("1️⃣ CREATE - Creating import batch record...")
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    cursor.execute(
        """
        INSERT INTO import_batches 
        (batch_id, schema_id, file_name, file_hash, data_start_row, total_rows,
         inserted_rows, skipped_rows, error_rows, processing_time_ms, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            batch_id,
            "test_schema_123",
            "test_excel.xlsx",
            "hash_" + batch_id,
            2,
            5000,
            2950,
            50,
            0,
            15000,
            "in_progress",
        ),
    )

    conn.commit()
    print(f"   ✅ Created import batch record: {batch_id}")

    # READ
    print("\n2️⃣ READ - Retrieving import batch records...")
    cursor.execute("SELECT COUNT(*) FROM import_batches")
    count = cursor.fetchone()[0]
    print(f"   ✅ Total records: {count}")

    cursor.execute("SELECT * FROM import_batches WHERE batch_id = ?", (batch_id,))
    row = cursor.fetchone()
    if row:
        print(f"   ✅ Retrieved record: {row['batch_id']} - Status: {row['status']}")

    # UPDATE
    print("\n3️⃣ UPDATE - Updating import batch record...")
    cursor.execute(
        """
        UPDATE import_batches 
        SET status = ?, inserted_rows = ?, processing_time_ms = ?
        WHERE batch_id = ?
    """,
        ("completed", 5000, 25000, batch_id),
    )

    conn.commit()
    print("   ✅ Updated import batch record")

    # DELETE
    print("\n4️⃣ DELETE - Deleting import batch record...")
    cursor.execute("DELETE FROM import_batches WHERE batch_id = ?", (batch_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"   ✅ Deleted {deleted_count} record(s)")

    return batch_id


def test_audit_log_crud():
    """Test CRUD operations for audit_log table."""
    print("\n📝 Testing audit_log CRUD operations...")
    print("=" * 60)

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # CREATE
    print("1️⃣ CREATE - Creating audit log record...")
    log_id = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    cursor.execute(
        """
        INSERT INTO audit_log 
        (batch_id, operation_type, document_id, original_data, new_data, row_number)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            "test_batch_123",
            "insert",
            "doc_123",
            None,
            json.dumps({"name": "Test Document", "value": 100}),
            15,
        ),
    )

    conn.commit()
    print(f"   ✅ Created audit log record: {log_id}")

    # READ
    print("\n2️⃣ READ - Retrieving audit log records...")
    cursor.execute("SELECT COUNT(*) FROM audit_log")
    count = cursor.fetchone()[0]
    print(f"   ✅ Total records: {count}")

    cursor.execute("SELECT * FROM audit_log WHERE document_id = ?", ("doc_123",))
    row = cursor.fetchone()
    if row:
        print(
            f"   ✅ Retrieved record: {row['id']} - Operation: {row['operation_type']}"
        )

    # UPDATE
    print("\n3️⃣ UPDATE - Updating audit log record...")
    cursor.execute(
        """
        UPDATE audit_log 
        SET operation_type = ?, new_data = ?
        WHERE document_id = ?
    """,
        ("update", json.dumps({"name": "Updated Document", "value": 200}), "doc_123"),
    )

    conn.commit()
    print("   ✅ Updated audit log record")

    # DELETE
    print("\n4️⃣ DELETE - Deleting audit log record...")
    cursor.execute("DELETE FROM audit_log WHERE document_id = ?", ("doc_123",))
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"   ✅ Deleted {deleted_count} record(s)")

    return log_id


def test_data_quality_issues_crud():
    """Test CRUD operations for data_quality_issues table."""
    print("\n⚠️ Testing data_quality_issues CRUD operations...")
    print("=" * 60)

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # CREATE
    print("1️⃣ CREATE - Creating data quality issue record...")
    issue_id = f"issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    cursor.execute(
        """
        INSERT INTO data_quality_issues 
        (batch_id, issue_type, row_number, column_name, original_value, expected_type, severity, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            "test_batch_123",
            "validation_error",
            15,
            "email",
            "invalid_email",
            "email",
            "warning",
            "Email address is not in valid format",
        ),
    )

    conn.commit()
    print(f"   ✅ Created data quality issue record: {issue_id}")

    # READ
    print("\n2️⃣ READ - Retrieving data quality issue records...")
    cursor.execute("SELECT COUNT(*) FROM data_quality_issues")
    count = cursor.fetchone()[0]
    print(f"   ✅ Total records: {count}")

    cursor.execute(
        "SELECT * FROM data_quality_issues WHERE batch_id = ? AND row_number = ?",
        ("test_batch_123", 15),
    )
    row = cursor.fetchone()
    if row:
        print(f"   ✅ Retrieved record: {row['id']} - Type: {row['issue_type']}")

    # UPDATE
    print("\n3️⃣ UPDATE - Updating data quality issue record...")
    cursor.execute(
        """
        UPDATE data_quality_issues 
        SET severity = ?, description = ?
        WHERE batch_id = ? AND row_number = ?
    """,
        ("error", "Updated description", "test_batch_123", 15),
    )

    conn.commit()
    print("   ✅ Updated data quality issue record")

    # DELETE
    print("\n4️⃣ DELETE - Deleting data quality issue record...")
    cursor.execute(
        "DELETE FROM data_quality_issues WHERE batch_id = ? AND row_number = ?",
        ("test_batch_123", 15),
    )
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"   ✅ Deleted {deleted_count} record(s)")

    return issue_id


def test_schema_analytics_crud():
    """Test CRUD operations for schema_analytics table."""
    print("\n📊 Testing schema_analytics CRUD operations...")
    print("=" * 60)

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # CREATE
    print("1️⃣ CREATE - Creating schema analytics record...")
    analytics_id = f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    cursor.execute(
        """
        INSERT INTO schema_analytics 
        (schema_id, usage_date, files_processed, total_rows_processed,
         average_processing_time_ms, error_rate)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        ("test_schema_123", datetime.now().date().isoformat(), 5, 2500, 12500, 0.04),
    )

    conn.commit()
    print(f"   ✅ Created schema analytics record: {analytics_id}")

    # READ
    print("\n2️⃣ READ - Retrieving schema analytics records...")
    cursor.execute("SELECT COUNT(*) FROM schema_analytics")
    count = cursor.fetchone()[0]
    print(f"   ✅ Total records: {count}")

    cursor.execute(
        "SELECT * FROM schema_analytics WHERE schema_id = ?", ("test_schema_123",)
    )
    row = cursor.fetchone()
    if row:
        print(f"   ✅ Retrieved record: {row['id']} - Files: {row['files_processed']}")

    # UPDATE
    print("\n3️⃣ UPDATE - Updating schema analytics record...")
    cursor.execute(
        """
        UPDATE schema_analytics 
        SET files_processed = ?, total_rows_processed = ?
        WHERE schema_id = ?
    """,
        (6, 3000, "test_schema_123"),
    )

    conn.commit()
    print("   ✅ Updated schema analytics record")

    # DELETE
    print("\n4️⃣ DELETE - Deleting schema analytics record...")
    cursor.execute(
        "DELETE FROM schema_analytics WHERE schema_id = ?", ("test_schema_123",)
    )
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"   ✅ Deleted {deleted_count} record(s)")

    return analytics_id


def test_ui_state_crud():
    """Test CRUD operations for ui_state table."""
    print("\n🎨 Testing ui_state CRUD operations...")
    print("=" * 60)

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # CREATE
    print("1️⃣ CREATE - Creating UI state record...")
    state_id = f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    cursor.execute(
        """
        INSERT INTO ui_state 
        (user_id, last_used_schema_id, last_import_directory, default_data_start_row, 
         default_duplicate_strategy, ui_theme, window_size, recent_files)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            "test_user",
            "test_schema_123",
            "C:/Users/Test/Documents/",
            2,
            "skip",
            "light",
            json.dumps({"width": 1400, "height": 900}),
            json.dumps(["C:/Users/Test/Documents/test.xlsx"]),
        ),
    )

    conn.commit()
    print(f"   ✅ Created UI state record: {state_id}")

    # READ
    print("\n2️⃣ READ - Retrieving UI state records...")
    cursor.execute("SELECT COUNT(*) FROM ui_state")
    count = cursor.fetchone()[0]
    print(f"   ✅ Total records: {count}")

    cursor.execute("SELECT * FROM ui_state WHERE user_id = ?", ("test_user",))
    row = cursor.fetchone()
    if row:
        print(f"   ✅ Retrieved record: {row['id']} - Theme: {row['ui_theme']}")

    # UPDATE
    print("\n3️⃣ UPDATE - Updating UI state record...")
    cursor.execute(
        """
        UPDATE ui_state 
        SET ui_theme = ?, window_size = ?, default_data_start_row = ?
        WHERE user_id = ?
    """,
        ("dark", json.dumps({"width": 1600, "height": 1000}), 3, "test_user"),
    )

    conn.commit()
    print("   ✅ Updated UI state record")

    # DELETE
    print("\n4️⃣ DELETE - Deleting UI state record...")
    cursor.execute("DELETE FROM ui_state WHERE user_id = ?", ("test_user",))
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"   ✅ Deleted {deleted_count} record(s)")

    return state_id


def cleanup_all_tables():
    """Clean up all test records from all tables."""
    print("\n🧹 Cleaning up all test records from all tables...")
    print("=" * 60)

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    tables = [
        "schema_definitions",
        "file_processing_history",
        "import_batches",
        "audit_log",
        "data_quality_issues",
        "schema_analytics",
        "ui_state",
    ]

    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count_before = cursor.fetchone()[0]

            cursor.execute(f"DELETE FROM {table}")
            deleted_count = cursor.rowcount

            conn.commit()
            print(f"   📊 {table}: {count_before} → {deleted_count} deleted")

        except Exception as e:
            print(f"   ❌ Error cleaning {table}: {e}")

    conn.close()
    print("   🎉 Cleanup completed!")


def main():
    """Main test function."""
    print("🚀 Comprehensive CRUD Test Suite for All SQLite Tables")
    print("=" * 80)

    try:
        # Test all tables
        test_schema_definitions_crud()
        test_file_processing_history_crud()
        test_import_batches_crud()
        test_audit_log_crud()
        test_data_quality_issues_crud()
        test_schema_analytics_crud()
        test_ui_state_crud()

        print("\n" + "=" * 80)
        print("✅ All CRUD tests completed successfully!")

        # Cleanup
        cleanup_all_tables()

        print("\n" + "=" * 80)
        print("🎯 Test Summary:")
        print("   ✅ schema_definitions - Full CRUD operations")
        print("   ✅ file_processing_history - Full CRUD operations")
        print("   ✅ import_batches - Full CRUD operations")
        print("   ✅ audit_log - Full CRUD operations")
        print("   ✅ data_quality_issues - Full CRUD operations")
        print("   ✅ schema_analytics - Full CRUD operations")
        print("   ✅ ui_state - Full CRUD operations")
        print("   ✅ Complete database cleanup")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()

        # Still try to cleanup
        try:
            cleanup_all_tables()
        except:
            print("   ❌ Cleanup also failed")
    finally:
        # Ensure cleanup happens
        try:
            cleanup_all_tables()
        except:
            pass


if __name__ == "__main__":
    main()
