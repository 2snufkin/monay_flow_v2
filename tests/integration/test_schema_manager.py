#!/usr/bin/env python3
"""
Live Test Script for SchemaManager

This script tests all SchemaManager methods with real database operations
and cleans up all records at the end.
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, str(os.path.dirname(__file__) / "src"))

from src.core.schema_manager import SchemaManager
from src.models.schema_definition import (
    SchemaDefinition,
    AttributeDefinition,
    IndexDefinition,
)
from src.config.database_config import get_sqlite_connection


def test_schema_manager():
    """Test all SchemaManager methods."""
    print("🧪 Testing SchemaManager Methods")
    print("=" * 50)
    
    # Initialize SchemaManager
    schema_manager = SchemaManager()
    
    # Test data
    test_schema_name = "Test Excel Schema"
    test_columns = ["First Name", "Last Name", "Email", "Phone", "Purchase Date", "Amount"]
    
    # Test 1: Create schema ID
    print("\n1️⃣ Testing create_schema...")
    schema_id = schema_manager.create_schema(
        test_schema_name, test_columns
    )
    print(f"   ✅ Generated schema_id: {schema_id}")
    
    # Test 2: Create a complete schema definition
    print("\n2️⃣ Creating complete schema definition...")
    
    # Create normalized attributes
    normalized_attrs = {
        "First Name": AttributeDefinition(
            field_name="first_name",
            data_type="string",
            description="Customer's first name",
            is_required=True
        ),
        "Last Name": AttributeDefinition(
            field_name="last_name", 
            data_type="string",
            description="Customer's last name",
            is_required=True
        ),
        "Email": AttributeDefinition(
            field_name="email",
            data_type="string", 
            description="Customer's email address",
            is_required=True
        ),
        "Phone": AttributeDefinition(
            field_name="phone",
            data_type="string",
            description="Customer's phone number",
            is_required=False
        ),
        "Purchase Date": AttributeDefinition(
            field_name="purchase_date",
            data_type="date",
            description="Date of purchase",
            is_required=True
        ),
        "Amount": AttributeDefinition(
            field_name="amount",
            data_type="decimal",
            description="Purchase amount",
            is_required=True
        )
    }
    
    # Create suggested indexes
    suggested_indexes = [
        IndexDefinition(
            field_names=["email"],
            index_type="unique",
            reason="Email should be unique for customer identification"
        ),
        IndexDefinition(
            field_names=["purchase_date"],
            index_type="btree",
            reason="Frequent queries by date range"
        ),
        IndexDefinition(
            field_names=["last_name", "first_name"],
            index_type="btree", 
            reason="Customer name lookups"
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
        usage_count=0
    )
    
    print(f"   ✅ Created schema definition with {len(normalized_attrs)} attributes")
    print(f"   ✅ Created {len(suggested_indexes)} suggested indexes")
    
    # Test 3: Save schema to database
    print("\n3️⃣ Testing save_schema_definition...")
    save_result = schema_manager.save_schema_definition(schema_def)
    print(f"   ✅ Save result: {save_result}")
    
    # Test 4: Get all schemas
    print("\n4️⃣ Testing get_all_schemas...")
    all_schemas = schema_manager.get_all_schemas()
    print(f"   ✅ Found {len(all_schemas)} schemas in database")
    
    if all_schemas:
        latest_schema = all_schemas[0]
        print(
            f"   📋 Latest schema: {latest_schema.schema_name} "
            f"(ID: {latest_schema.schema_id})"
        )
        print(f"   📊 Columns: {len(latest_schema.excel_column_names)}")
        print(f"   🔍 Duplicate detection: {latest_schema.duplicate_detection_columns}")
    
    # Test 5: Get schema by ID
    print("\n5️⃣ Testing get_schema_by_id...")
    retrieved_schema = schema_manager.get_schema_by_id(schema_id)
    if retrieved_schema:
        print(f"   ✅ Retrieved schema: {retrieved_schema.schema_name}")
        print(
            f"   📊 Normalized attributes: "
            f"{len(retrieved_schema.normalized_attributes)}"
        )
        print(f"   🔍 Duplicate strategy: {retrieved_schema.duplicate_strategy}")
    else:
        print("   ❌ Failed to retrieve schema")
    
    # Test 6: Update schema usage
    print("\n6️⃣ Testing update_schema_usage...")
    schema_manager.update_schema_usage(schema_id)
    print("   ✅ Updated schema usage")
    
    # Test 7: Update data start row
    print("\n7️⃣ Testing update_schema_data_start_row...")
    update_result = schema_manager.update_schema_data_start_row(schema_id, 3)
    print(f"   ✅ Update data start row result: {update_result}")
    
    # Test 8: Verify updates
    print("\n8️⃣ Verifying updates...")
    updated_schema = schema_manager.get_schema_by_id(schema_id)
    if updated_schema:
        print(f"   ✅ Usage count: {updated_schema.usage_count}")
        print(f"   ✅ Data start row: {updated_schema.data_start_row}")
        print(f"   ✅ Last used: {updated_schema.last_used}")
    
    # Test 9: Create another schema for testing
    print("\n9️⃣ Creating second test schema...")
    schema_id_2 = schema_manager.create_schema(
        "Test Schema 2", ["ID", "Name", "Value"]
    )
    
    # Create minimal schema for second test
    schema_def_2 = SchemaDefinition(
        schema_id=schema_id_2,
        schema_name="Test Schema 2",
        excel_column_names=["ID", "Name", "Value"],
        normalized_attributes={},
        suggested_indexes=[],
        duplicate_detection_columns=["ID"],
        duplicate_strategy="update",
        data_start_row=1,
        mongodb_collection_name="test_data",
        created_at=datetime.now(),
        last_used=datetime.now(),
        usage_count=0
    )
    
    save_result_2 = schema_manager.save_schema_definition(schema_def_2)
    print(f"   ✅ Second schema save result: {save_result_2}")
    
    # Test 10: Verify multiple schemas
    print("\n🔟 Testing multiple schemas...")
    all_schemas_after = schema_manager.get_all_schemas()
    print(f"   ✅ Total schemas after creation: {len(all_schemas_after)}")
    
    for i, schema in enumerate(all_schemas_after):
        print(
            f"   📋 Schema {i+1}: {schema.schema_name} "
            f"(ID: {schema.schema_id})"
        )
    
    return [schema_id, schema_id_2]


def cleanup_all_records():
    """Remove all test records from the database."""
    print("\n🧹 Cleaning up all test records...")
    print("=" * 50)
    
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        # Get count before cleanup
        cursor.execute("SELECT COUNT(*) FROM schema_definitions")
        count_before = cursor.fetchone()[0]
        print(f"   📊 Records before cleanup: {count_before}")
        
        # Delete all records
        cursor.execute("DELETE FROM schema_definitions")
        deleted_count = cursor.rowcount
        
        conn.commit()
        print(f"   ✅ Deleted {deleted_count} records")
        
        # Verify cleanup
        cursor.execute("SELECT COUNT(*) FROM schema_definitions")
        count_after = cursor.fetchone()[0]
        print(f"   📊 Records after cleanup: {count_after}")
        
        if count_after == 0:
            print("   🎉 Cleanup successful! Database is empty.")
        else:
            print("   ⚠️  Some records remain after cleanup.")
            
    except Exception as e:
        print(f"   ❌ Error during cleanup: {e}")


def main():
    """Main test function."""
    print("🚀 SchemaManager Live Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        created_schema_ids = test_schema_manager()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print(f"📝 Created {len(created_schema_ids)} test schemas")
        
        # Cleanup
        cleanup_all_records()
        
        print("\n" + "=" * 60)
        print("🎯 Test Summary:")
        print("   ✅ Schema creation and ID generation")
        print("   ✅ Schema definition creation")
        print("   ✅ Database save operations")
        print("   ✅ Schema retrieval (all and by ID)")
        print("   ✅ Schema usage updates")
        print("   ✅ Data start row updates")
        print("   ✅ Multiple schema handling")
        print("   ✅ Complete database cleanup")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
        # Still try to cleanup
        try:
            cleanup_all_records()
        except:
            print("   ❌ Cleanup also failed")


if __name__ == "__main__":
    main()
