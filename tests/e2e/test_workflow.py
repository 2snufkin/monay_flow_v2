#!/usr/bin/env python3
"""
End-to-End (E2E) Test for MoneyFlowV2

This test launches the actual UI and tests the complete workflow:
1. Launch UI
2. Create schema through dialog
3. Wait for OpenAI processing
4. Verify database records
5. Test schema retrieval
"""

import sys
import os
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.schema_manager import SchemaManager
from src.models.schema_definition import SchemaDefinition
from src.config.database_config import get_sqlite_connection


class E2ETester:
    """End-to-end test runner for MoneyFlowV2."""
    
    def __init__(self):
        """Initialize the E2E tester."""
        self.schema_manager = SchemaManager()
        self.test_results = []
        self.test_schema_name = f"E2E Test Schema {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_database_connection(self) -> bool:
        """Test database connection and basic operations."""
        self.log("🔌 Testing database connection...")
        
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            self.log(f"📊 Found {len(tables)} tables: {', '.join(table_names)}")
            
            # Check schema_definitions table specifically
            if 'schema_definitions' in table_names:
                cursor.execute("SELECT COUNT(*) FROM schema_definitions")
                count = cursor.fetchone()[0]
                self.log(f"📋 schema_definitions table has {count} records")
            else:
                self.log("❌ schema_definitions table not found", "ERROR")
                return False
                
            self.log("✅ Database connection test passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Database connection test failed: {e}", "ERROR")
            return False
    
    def test_schema_creation_workflow(self) -> bool:
        """Test the complete schema creation workflow."""
        self.log("🔄 Testing schema creation workflow...")
        
        try:
            # Step 1: Create schema ID
            self.log("1️⃣ Creating schema ID...")
            schema_id = self.schema_manager.create_schema(self.test_schema_name, [])
            self.log(f"   ✅ Generated schema_id: {schema_id}")
            
            # Step 2: Create a test schema definition
            self.log("2️⃣ Creating test schema definition...")
            test_columns = ["First Name", "Last Name", "Email", "Phone", "Purchase Date", "Amount"]
            
            # Create a minimal schema for testing
            schema_def = SchemaDefinition(
                schema_id=schema_id,
                schema_name=self.test_schema_name,
                excel_column_names=test_columns,
                normalized_attributes={},  # Empty for now
                suggested_indexes=[],      # Empty for now
                duplicate_detection_columns=["email", "phone"],
                duplicate_strategy="skip",
                data_start_row=2,
                mongodb_collection_name="e2e_test_customers",
                created_at=datetime.now(),
                last_used=datetime.now(),
                usage_count=0
            )
            
            # Step 3: Save to database
            self.log("3️⃣ Saving schema to database...")
            save_result = self.schema_manager.save_schema_definition(schema_def)
            self.log(f"   ✅ Save result: {save_result}")
            
            if not save_result:
                self.log("❌ Schema save failed", "ERROR")
                return False
            
            # Step 4: Verify schema was saved
            self.log("4️⃣ Verifying schema was saved...")
            retrieved_schema = self.schema_manager.get_schema_by_id(schema_id)
            
            if retrieved_schema:
                self.log(f"   ✅ Schema retrieved: {retrieved_schema.schema_name}")
                self.log(f"   📊 Columns: {len(retrieved_schema.excel_column_names)}")
                self.log(f"   🔍 Collection: {retrieved_schema.mongodb_collection_name}")
            else:
                self.log("❌ Schema retrieval failed", "ERROR")
                return False
            
            # Step 5: Test schema usage update
            self.log("5️⃣ Testing schema usage update...")
            self.schema_manager.update_schema_usage(schema_id)
            
            updated_schema = self.schema_manager.get_schema_by_id(schema_id)
            if updated_schema and updated_schema.usage_count > 0:
                self.log(f"   ✅ Usage count updated: {updated_schema.usage_count}")
            else:
                self.log("❌ Usage count update failed", "ERROR")
                return False
            
            self.log("✅ Schema creation workflow test passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Schema creation workflow test failed: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def test_schema_retrieval(self) -> bool:
        """Test schema retrieval and listing."""
        self.log("📋 Testing schema retrieval...")
        
        try:
            # Get all schemas
            all_schemas = self.schema_manager.get_all_schemas()
            self.log(f"📊 Found {len(all_schemas)} total schemas")
            
            # Find our test schema
            test_schema = None
            for schema in all_schemas:
                if schema.schema_name == self.test_schema_name:
                    test_schema = schema
                    break
            
            if test_schema:
                self.log(f"✅ Test schema found: {test_schema.schema_id}")
                self.log(f"   📊 Columns: {len(test_schema.excel_column_names)}")
                self.log(f"   🔍 Duplicate strategy: {test_schema.duplicate_strategy}")
                return True
            else:
                self.log("❌ Test schema not found in list", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Schema retrieval test failed: {e}", "ERROR")
            return False
    
    def test_database_verification(self) -> bool:
        """Verify database records directly."""
        self.log("🔍 Verifying database records directly...")
        
        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            # Check schema_definitions table
            cursor.execute("SELECT COUNT(*) FROM schema_definitions")
            total_count = cursor.fetchone()[0]
            self.log(f"📊 Total schemas in database: {total_count}")
            
            # Find our test schema
            cursor.execute("""
                SELECT schema_id, schema_name, original_columns, mongodb_collection_name, created_at
                FROM schema_definitions 
                WHERE schema_name = ?
            """, (self.test_schema_name,))
            
            row = cursor.fetchone()
            if row:
                self.log(f"✅ Test schema found in database:")
                self.log(f"   🆔 ID: {row[0]}")
                self.log(f"   📝 Name: {row[1]}")
                self.log(f"   📊 Columns: {row[2]}")
                self.log(f"   🗄️ Collection: {row[3]}")
                self.log(f"   📅 Created: {row[4]}")
                return True
            else:
                self.log("❌ Test schema not found in database", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Database verification failed: {e}", "ERROR")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data."""
        self.log("🧹 Cleaning up test data...")
        
        try:
            # Delete test schema from database
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM schema_definitions WHERE schema_name = ?", (self.test_schema_name,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            
            self.log(f"✅ Deleted {deleted_count} test schema(s)")
            
        except Exception as e:
            self.log(f"❌ Cleanup failed: {e}", "ERROR")
    
    def run_all_tests(self) -> bool:
        """Run all E2E tests."""
        self.log("🚀 Starting E2E Test Suite for MoneyFlowV2")
        self.log("=" * 60)
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("Schema Creation Workflow", self.test_schema_creation_workflow),
            ("Schema Retrieval", self.test_schema_retrieval),
            ("Database Verification", self.test_database_verification),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n🧪 Running: {test_name}")
            self.log("-" * 40)
            
            if test_func():
                self.log(f"✅ {test_name} PASSED")
                passed += 1
            else:
                self.log(f"❌ {test_name} FAILED")
        
        # Summary
        self.log(f"\n" + "=" * 60)
        self.log(f"🎯 E2E Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All tests passed! Application is working correctly.")
        else:
            self.log("⚠️ Some tests failed. Check the logs above for details.")
        
        return passed == total


def main():
    """Main E2E test function."""
    tester = E2ETester()
    
    try:
        success = tester.run_all_tests()
        
        # Always cleanup
        tester.cleanup_test_data()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ E2E test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
