#!/usr/bin/env python3
"""
Clear Excel Schemas Collection

This script empties the excel_schemas.schemas collection in MongoDB.
Useful for cleaning up test data and starting fresh.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

import logging
from pymongo import MongoClient
from config.settings import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_schemas_collection():
    """Clear all documents from the excel_schemas.schemas collection."""
    try:
        settings = get_settings()
        client = MongoClient(settings.database.mongo_url)
        
        # Connect to excel_schemas database
        db = client.excel_schemas
        collection = db.schemas
        
        # Get count before deletion
        count_before = collection.count_documents({})
        logger.info(f"Found {count_before} documents in excel_schemas.schemas collection")
        
        if count_before == 0:
            logger.info("Collection is already empty")
            return True
            
        # Delete all documents
        result = collection.delete_many({})
        logger.info(f"Deleted {result.deleted_count} documents from excel_schemas.schemas")
        
        # Verify deletion
        count_after = collection.count_documents({})
        logger.info(f"Collection now contains {count_after} documents")
        
        if count_after == 0:
            logger.info("✅ Successfully cleared excel_schemas.schemas collection")
            return True
        else:
            logger.error(f"❌ Failed to clear collection completely. {count_after} documents remain")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error clearing collection: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()


def list_all_schemas():
    """List all schemas in the collection before clearing."""
    try:
        settings = get_settings()
        client = MongoClient(settings.database.mongo_url)
        
        db = client.excel_schemas
        collection = db.schemas
        
        schemas = list(collection.find({}, {"schema_name": 1, "database_name": 1, "created_at": 1}))
        
        if schemas:
            logger.info(f"\n📋 Current schemas in collection ({len(schemas)} total):")
            for i, schema in enumerate(schemas, 1):
                name = schema.get('schema_name', 'Unknown')
                db_name = schema.get('database_name', 'Unknown')
                created = schema.get('created_at', 'Unknown')
                logger.info(f"  {i}. {name} -> {db_name} (created: {created})")
        else:
            logger.info("📋 No schemas found in collection")
            
        return schemas
        
    except Exception as e:
        logger.error(f"❌ Error listing schemas: {e}")
        return []
    finally:
        if 'client' in locals():
            client.close()


def main():
    """Main function."""
    logger.info("🧹 Excel Schemas Collection Cleaner")
    logger.info("=" * 50)
    
    # First, list current schemas
    schemas = list_all_schemas()
    
    if not schemas:
        logger.info("✅ Collection is already empty, nothing to clear")
        return
    
    # Confirm deletion
    print(f"\n⚠️  This will delete ALL {len(schemas)} schemas from excel_schemas.schemas collection")
    response = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        logger.info("🗑️  Proceeding with deletion...")
        success = clear_schemas_collection()
        
        if success:
            logger.info("🎉 Collection cleared successfully!")
        else:
            logger.error("💥 Failed to clear collection")
            sys.exit(1)
    else:
        logger.info("❌ Operation cancelled by user")


if __name__ == "__main__":
    main()
