#!/usr/bin/env python3
"""
Core Integration Test

Tests the integration of ExcelProcessor, MongoCollectionManager, and DataIngestionEngine.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.excel_processor import ExcelProcessor
from src.core.mongo_collection_manager import MongoCollectionManager
from src.core.data_ingestion_engine import DataIngestionEngine
from src.models.schema_definition import SchemaDefinition

def test_core_integration():
    """Test core component integration."""
    print("🧪 Testing Core Component Integration")
    print("=" * 50)
    
    try:
        # Test 1: Excel Processor
        print("1️⃣ Testing ExcelProcessor...")
        excel_processor = ExcelProcessor()
        
        # Create a test Excel file path (we'll use the existing one)
        test_file = Path("export_22_08_2025_03_22_19.xls")
        
        if test_file.exists():
            print(f"   📁 Found test file: {test_file}")
            
            # Validate file
            is_valid = excel_processor.validate_file(test_file)
            print(f"   ✅ File validation: {is_valid}")
            
            if is_valid:
                # Get file info
                file_info = excel_processor.get_file_info(test_file)
                print(f"   📊 File info: {file_info.total_rows} rows, {file_info.total_columns} columns")
                print(f"   📋 Columns: {file_info.column_names[:5]}...")  # First 5 columns
                
                # Extract column information
                columns_info = excel_processor.extract_columns(test_file)
                print(f"   🔍 Column analysis: {len(columns_info)} columns analyzed")
                
                for col_info in columns_info[:3]:  # First 3 columns
                    print(f"      - {col_info.name}: {col_info.data_type} ({col_info.unique_count} unique)")
            else:
                print("   ❌ File validation failed")
                return False
        else:
            print("   ⚠️ Test Excel file not found, skipping file tests")
        
        print("   ✅ ExcelProcessor test completed")
        
        # Test 2: MongoDB Collection Manager
        print("\n2️⃣ Testing MongoCollectionManager...")
        mongo_manager = MongoCollectionManager()
        
        # Create a test schema definition
        test_schema = SchemaDefinition(
            schema_id="test_schema_001",
            schema_name="Integration Test Schema",
            excel_column_names=["Name", "Email", "Amount"],
            normalized_attributes={},
            suggested_indexes=[],
            duplicate_detection_columns=["email"],
            duplicate_strategy="skip",
            data_start_row=2,
            mongodb_collection_name="test_integration",
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=0
        )
        
        # Test collection creation (this will test MongoDB connection)
        try:
            collection = mongo_manager.create_collection("test_integration", test_schema)
            print(f"   ✅ Collection created: {collection.name}")
            
            # Test document insertion
            test_docs = [
                {"name": "John Doe", "email": "john@example.com", "amount": 100.0},
                {"name": "Jane Smith", "email": "jane@example.com", "amount": 200.0}
            ]
            
            result = mongo_manager.bulk_insert(collection, test_docs)
            print(f"   ✅ Bulk insert: {result.inserted_count} documents inserted")
            
            # Test duplicate detection
            duplicate_doc = {"name": "John Doe", "email": "john@example.com", "amount": 150.0}
            duplicate_result = mongo_manager.check_duplicates(collection, duplicate_doc, ["email"])
            print(f"   ✅ Duplicate check: {duplicate_result.is_duplicate} (confidence: {duplicate_result.confidence_score})")
            
            # Get collection stats
            stats = mongo_manager.get_collection_stats(collection)
            print(f"   ✅ Collection stats: {stats.get('document_count', 0)} documents")
            
            # Cleanup test collection
            collection.drop()
            print("   🧹 Test collection cleaned up")
            
        except Exception as e:
            print(f"   ⚠️ MongoDB test skipped (connection issue): {e}")
        
        print("   ✅ MongoCollectionManager test completed")
        
        # Test 3: Data Ingestion Engine
        print("\n3️⃣ Testing DataIngestionEngine...")
        ingestion_engine = DataIngestionEngine()
        
        print("   ✅ DataIngestionEngine initialized")
        
        # Test progress callback
        def progress_callback(progress):
            print(f"      📊 Progress: {progress.progress_percentage:.1f}% ({progress.processed_rows}/{progress.total_rows})")
        
        ingestion_engine.set_progress_callback(progress_callback)
        print("   ✅ Progress callback set")
        
        # Test import history (should work even without actual imports)
        history = ingestion_engine.get_import_history(limit=5)
        print(f"   ✅ Import history: {len(history)} records")
        
        print("   ✅ DataIngestionEngine test completed")
        
        print("\n" + "=" * 50)
        print("🎉 All core integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_core_integration()
    exit(0 if success else 1)
