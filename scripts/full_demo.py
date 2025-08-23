#!/usr/bin/env python3
"""
Full MoneyFlow App Demo

Complete demonstration of the app's functionality including:
- Excel processing
- AI schema generation
- MongoDB storage
- Duplicate detection
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Also add the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Run complete app demo."""
    print("🚀 MoneyFlow Complete App Demo")
    print("=" * 60)
    
    try:
        from core.excel_processor import ExcelProcessor
        from core.ai_processor import AISchemaProcessor
        from core.schema_manager import SchemaManager
        from core.mongo_manager import MongoCollectionManager
        from config.settings import validate_settings
        from models.schema_definition import SchemaDefinition, AttributeDefinition, IndexDefinition
        
        # Step 1: Validate settings
        print("🔧 Step 1: Validating settings...")
        if not validate_settings():
            print("❌ Settings validation failed")
            return 1
        print("✅ Settings validation passed")
        
        # Step 2: Initialize components
        print("\n🚀 Step 2: Initializing components...")
        excel_processor = ExcelProcessor()
        ai_processor = AISchemaProcessor()
        schema_manager = SchemaManager()
        mongo_manager = MongoCollectionManager()
        print("✅ All components initialized")
        
        # Step 3: Check for Excel files
        print("\n📁 Step 3: Looking for Excel files...")
        excel_files = list(Path(".").glob("*.xls*"))
        if not excel_files:
            print("❌ No Excel files found")
            print("Please place an Excel file in the project directory")
            return 1
        
        excel_file = excel_files[0]
        print(f"✅ Found Excel file: {excel_file.name}")
        
        # Step 4: Process Excel file
        print(f"\n📊 Step 4: Processing Excel file: {excel_file.name}")
        
        # Get column names
        column_names = excel_processor.get_excel_column_names(str(excel_file))
        print(f"📋 Found {len(column_names)} columns:")
        for i, col in enumerate(column_names, 1):
            print(f"  {i}. {col}")
        
        # Get row count
        row_count = excel_processor.get_excel_row_count(str(excel_file))
        print(f"📊 Total rows: {row_count}")
        
        # Preview data
        print(f"\n👀 Data preview:")
        preview_data = excel_processor.preview_excel_data(str(excel_file), start_row=2, limit=2)
        for i, row in enumerate(preview_data, 1):
            print(f"  Row {i}: {dict(list(row.items())[:3])}...")  # Show first 3 fields
        
        # Step 5: AI Schema Processing
        print(f"\n🤖 Step 5: Using AI to process schema...")
        print("Sending column names to OpenAI for normalization...")
        
        try:
            ai_response = ai_processor.process_columns(column_names)
            print("✅ AI processing successful!")
            
            print(f"\n🏷️  Normalized attributes:")
            for orig_name, attr_def in ai_response.normalized_attributes.items():
                print(f"  '{orig_name}' → '{attr_def.field_name}' ({attr_def.data_type})")
            
            print(f"\n📑 Suggested indexes ({len(ai_response.suggested_indexes)}):")
            for idx in ai_response.suggested_indexes:
                print(f"  • {idx.field_names} ({idx.index_type})")
            
            print(f"\n🔍 Duplicate detection columns:")
            for col in ai_response.duplicate_detection_columns:
                print(f"  • {col}")
                
        except Exception as e:
            print(f"⚠️  AI processing failed: {e}")
            print("Continuing with manual schema...")
            # Create a simple manual schema
            ai_response = None
        
        # Step 6: Create Schema
        print(f"\n📋 Step 6: Creating schema definition...")
        
        if ai_response:
            # Use AI-generated schema
            schema_def = SchemaDefinition(
                schema_id=f"schema_{excel_file.stem}",
                schema_name=f"Schema for {excel_file.name}",
                excel_column_names=column_names,
                normalized_attributes=ai_response.normalized_attributes,
                suggested_indexes=ai_response.suggested_indexes,
                duplicate_detection_columns=ai_response.duplicate_detection_columns[:2],  # Use first 2
                duplicate_strategy="skip",
                data_start_row=2,
                created_at=None,  # Will be set by schema_manager
                last_used=None,   # Will be set by schema_manager
                usage_count=0
            )
        else:
            # Create simple manual schema
            normalized_attrs = {}
            for col in column_names:
                field_name = col.lower().replace(' ', '_').replace('-', '_')
                normalized_attrs[col] = AttributeDefinition(
                    field_name=field_name,
                    data_type="string",
                    is_required=False,
                    description=f"Field for {col}"
                )
            
            schema_def = SchemaDefinition(
                schema_id=f"schema_{excel_file.stem}",
                schema_name=f"Schema for {excel_file.name}",
                excel_column_names=column_names,
                normalized_attributes=normalized_attrs,
                suggested_indexes=[],
                duplicate_detection_columns=[column_names[0]] if column_names else [],
                duplicate_strategy="skip",
                data_start_row=2,
                created_at=None,
                last_used=None,
                usage_count=0
            )
        
        print(f"✅ Schema created: {schema_def.schema_name}")
        
        # Step 7: Save Schema
        print(f"\n💾 Step 7: Saving schema to database...")
        schema_id = schema_manager.save_schema_definition(schema_def)
        print(f"✅ Schema saved with ID: {schema_id}")
        
        # Step 8: Create MongoDB Collection
        print(f"\n🗄️  Step 8: Creating MongoDB collection...")
        collection_name = f"excel_{excel_file.stem}"
        
        success = mongo_manager.create_collection(collection_name, schema_def)
        if success:
            print(f"✅ MongoDB collection created: {collection_name}")
        else:
            print(f"⚠️  Collection may already exist: {collection_name}")
        
        # Step 9: Process and Insert Data
        print(f"\n📥 Step 9: Inserting data into MongoDB...")
        
        # Read data in batches
        batch_count = 0
        total_inserted = 0
        
        for batch in excel_processor.read_excel_file_stream(str(excel_file), start_row=2, batch_size=5):
            batch_count += 1
            print(f"  Processing batch {batch_count} ({len(batch)} rows)...")
            
            # Transform data using schema mapping
            transformed_batch = []
            for row in batch:
                transformed_row = {}
                for excel_col, value in row.items():
                    if excel_col in schema_def.normalized_attributes:
                        mongo_field = schema_def.normalized_attributes[excel_col].field_name
                        transformed_row[mongo_field] = value
                    else:
                        # Fallback for unmapped columns
                        transformed_row[excel_col.lower().replace(' ', '_')] = value
                
                transformed_batch.append(transformed_row)
            
            # Insert batch
            try:
                result = mongo_manager.bulk_insert_documents(collection_name, transformed_batch)
                total_inserted += result.inserted_count
                print(f"    ✅ Inserted {result.inserted_count} documents")
            except Exception as e:
                print(f"    ❌ Insert failed: {e}")
        
        print(f"✅ Total documents inserted: {total_inserted}")
        
        # Step 10: Verify Data
        print(f"\n🔍 Step 10: Verifying data in MongoDB...")
        stats = mongo_manager.get_collection_stats(collection_name)
        print(f"✅ Collection stats:")
        print(f"  • Documents: {stats.document_count}")
        print(f"  • Indexes: {len(stats.indexes)}")
        print(f"  • Storage size: {stats.storage_size_bytes} bytes")
        
        print(f"\n🎯 Demo Complete! Your Excel data has been successfully:")
        print("✅ Processed and validated")
        print("✅ Schema created with AI assistance")
        print("✅ Stored in MongoDB with proper indexing")
        print("✅ Ready for querying and analysis")
        
        print(f"\n📊 Summary:")
        print(f"  • Excel file: {excel_file.name}")
        print(f"  • Columns: {len(column_names)}")
        print(f"  • Rows processed: {total_inserted}")
        print(f"  • MongoDB collection: {collection_name}")
        print(f"  • Schema ID: {schema_id}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

