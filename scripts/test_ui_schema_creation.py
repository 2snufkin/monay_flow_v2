#!/usr/bin/env python3
"""
Test UI Schema Creation

This script tests the schema creation functionality that was fixed.
It simulates the UI workflow to ensure schemas are properly created.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

import logging
from datetime import datetime
from models.schema_definition import SchemaDefinition, CollectionDefinition, AttributeDefinition, IndexDefinition
from core.schema_manager import SchemaManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_schema_creation():
    """Test creating a schema like the UI does."""
    try:
        logger.info("🧪 Testing UI Schema Creation")
        
        schema_manager = SchemaManager()
        
        # Create test data similar to what UI would create
        schema_name = "UI Test Schema"
        database_name = "ui_test_db"
        collection_name = "test_collection"
        
        # Create normalized attributes (simplified)
        normalized_attributes = {
            "Name": AttributeDefinition(
                field_name="name",
                data_type="string",
                is_required=True,
                description="Person name"
            ),
            "Age": AttributeDefinition(
                field_name="age",
                data_type="integer",
                is_required=False,
                description="Person age"
            ),
            "Email": AttributeDefinition(
                field_name="email",
                data_type="string",
                is_required=True,
                description="Email address"
            )
        }
        
        # Create suggested indexes
        suggested_indexes = [
            IndexDefinition(
                field_names=["email"],
                index_type="unique",
                reason="Unique email addresses"
            ),
            IndexDefinition(
                field_names=["name"],
                index_type="ascending",
                reason="Name lookup performance"
            )
        ]
        
        # Create schema definition (exactly like the UI does after fix)
        schema_def = SchemaDefinition(
            schema_id=f"schema_{schema_name.lower().replace(' ', '_')}",
            schema_name=schema_name,
            database_name=database_name,
            excel_column_names=["Name", "Age", "Email"],
            normalized_attributes=normalized_attributes,
            suggested_indexes=suggested_indexes,
            duplicate_detection_columns=["email"],
            duplicate_strategy="skip",
            data_start_row=2,
            collections=[
                CollectionDefinition(
                    name=collection_name,
                    description=f"Collection for {schema_name}",
                    created_at=datetime.now(),
                    document_count=0,
                    last_updated=datetime.now(),
                )
            ],
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=0,
        )
        
        logger.info(f"📝 Created schema definition: {schema_def.schema_name}")
        logger.info(f"🗄️ Database: {schema_def.database_name}")
        logger.info(f"📁 Collection: {schema_def.collections[0].name}")
        
        # Save schema (this should now work)
        result = schema_manager.save_schema_definition(schema_def)
        
        if result:
            logger.info("✅ Schema created successfully!")
            
            # Verify it was saved
            saved_schema = schema_manager.get_schema_by_name(schema_name)
            if saved_schema:
                logger.info("✅ Schema verified in database")
                logger.info(f"   Schema ID: {saved_schema.schema_id}")
                logger.info(f"   Database: {saved_schema.database_name}")
                logger.info(f"   Collections: {len(saved_schema.collections)}")
                return True
            else:
                logger.error("❌ Schema not found after creation")
                return False
        else:
            logger.error("❌ Failed to create schema")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    logger.info("🚀 Starting UI Schema Creation Test")
    logger.info("=" * 50)
    
    success = test_schema_creation()
    
    if success:
        logger.info("🎉 All tests passed! UI schema creation should work now.")
    else:
        logger.error("💥 Tests failed. UI schema creation needs more fixes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
