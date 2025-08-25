#!/usr/bin/env python3
"""
Check Collection Data and Insert Permanent Test Data

This script checks the contents of the test25 collection and inserts
some permanent test data that won't be cleaned up.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def check_and_insert_data():
    """Check collection data and insert permanent test data."""
    try:
        from config.database_config import get_mongo_collection

        print("🔍 Checking test25 collection data...")

        # Get the collection
        collection = get_mongo_collection("test25")

        # Count documents
        doc_count = collection.count_documents({})
        print(f"📊 Documents in test25 collection: {doc_count}")

        if doc_count == 0:
            print("📝 Collection is empty. Inserting permanent test data...")

            # Insert some permanent test data
            test_documents = [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-0101",
                    "purchase_date": "2025-08-25T10:00:00",
                    "amount": 99.99,
                    "excel_row": 1,
                    "imported_at": "2025-08-25T10:00:00",
                    "test_type": "permanent",
                },
                {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "email": "jane.smith@example.com",
                    "phone": "555-0102",
                    "purchase_date": "2025-08-25T11:00:00",
                    "amount": 149.99,
                    "excel_row": 2,
                    "imported_at": "2025-08-25T11:00:00",
                    "test_type": "permanent",
                },
                {
                    "first_name": "Bob",
                    "last_name": "Johnson",
                    "email": "bob.johnson@example.com",
                    "phone": "555-0103",
                    "purchase_date": "2025-08-25T12:00:00",
                    "amount": 79.99,
                    "excel_row": 3,
                    "imported_at": "2025-08-25T12:00:00",
                    "test_type": "permanent",
                },
            ]

            # Insert the documents
            result = collection.insert_many(test_documents)
            print(f"✅ Inserted {len(result.inserted_ids)} permanent test documents")

            # Create indexes
            collection.create_index("email", unique=True)
            collection.create_index("phone", unique=True)
            print("🔍 Created unique indexes on email and phone")

        else:
            print("📋 Collection has data. Showing first few documents:")
            # Show first few documents
            for doc in collection.find().limit(3):
                print(f"   📄 {doc['first_name']} {doc['last_name']} - {doc['email']}")

        # Final count
        final_count = collection.count_documents({})
        print(f"\n📊 Final document count: {final_count}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = check_and_insert_data()
    exit(0 if success else 1)
