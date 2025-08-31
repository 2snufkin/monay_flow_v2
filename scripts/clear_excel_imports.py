#!/usr/bin/env python3
"""
Clear Excel Imports Database Script

This script clears all data from the excel_imports database except the schemas collection,
as requested by the user.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.settings import get_settings
from pymongo import MongoClient


def clear_excel_imports_database():
    """Clear all data from excel_imports database except schemas collection."""
    try:
        print("🗄️ Clearing excel_imports database...")

        # Get settings
        settings = get_settings()
        mongo_url = settings.database.mongo_url

        if not mongo_url:
            print("❌ MongoDB URL not configured")
            return False

        # Connect to MongoDB
        client = MongoClient(mongo_url)
        db = client.excel_imports

        # Get all collections
        collections = db.list_collection_names()
        print(f"📋 Found collections: {collections}")

        # Clear all collections except schemas
        cleared_count = 0
        for collection_name in collections:
            if collection_name != "schemas":
                print(f"🗑️ Dropping collection: {collection_name}")
                db.drop_collection(collection_name)
                cleared_count += 1

        print(f"✅ Cleared {cleared_count} collections from excel_imports database")
        print("💾 Kept schemas collection for schema metadata")

        # Show remaining collections
        remaining = db.list_collection_names()
        print(f"📋 Remaining collections: {remaining}")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Failed to clear database: {e}")
        return False


def main():
    """Main function."""
    print("🧹 Excel Imports Database Cleanup")
    print("=" * 50)

    success = clear_excel_imports_database()

    if success:
        print("\n✅ Database cleanup completed successfully!")
        print("🎯 The excel_imports database is now clean and ready for new schemas")
    else:
        print("\n❌ Database cleanup failed!")
        print("🔍 Check the error messages above")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())


