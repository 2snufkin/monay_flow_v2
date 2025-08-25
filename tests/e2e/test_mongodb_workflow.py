#!/usr/bin/env python3
"""
MongoDB End-to-End (E2E) Test for MoneyFlowV2

This test focuses on the complete Excel-to-MongoDB workflow:
1. Create test Excel file with email data
2. Set up SQLite schema with email duplication validation
3. Process Excel file and save to MongoDB Atlas collection "test25"
4. Verify data integrity in both databases
5. Test duplicate detection and handling
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import random

# Load environment variables first
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.schema_manager import SchemaManager
from core.excel_processor import ExcelProcessor
from core.mongo_collection_manager import MongoCollectionManager
from core.data_ingestion_engine import DataIngestionEngine
from models.schema_definition import SchemaDefinition
from config.database_config import (
    get_sqlite_connection,
    get_mongo_database,
    get_mongo_collection,
)
from config.settings import get_settings


class MongoDBE2ETester:
    """MongoDB end-to-end test runner for MoneyFlowV2."""

    def __init__(self):
        """Initialize the MongoDB E2E tester."""
        self.schema_manager = SchemaManager()
        self.excel_processor = ExcelProcessor()
        self.mongo_manager = MongoCollectionManager()
        self.ingestion_engine = DataIngestionEngine()

        self.test_results = []
        self.test_schema_name = (
            f"MongoDB E2E Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.test_excel_file = Path("test_data_with_emails.xlsx")
        self.mongodb_collection_name = "test25"

        # Test data for Excel file
        self.test_data = {
            "First Name": [
                "John",
                "Jane",
                "Bob",
                "Alice",
                "Charlie",
                "Diana",
                "Eve",
                "Frank",
                "Grace",
                "Henry",
            ],
            "Last Name": [
                "Doe",
                "Smith",
                "Johnson",
                "Brown",
                "Wilson",
                "Davis",
                "Miller",
                "Garcia",
                "Martinez",
                "Anderson",
            ],
            "Email": [
                "john.doe@example.com",
                "jane.smith@example.com",
                "bob.johnson@example.com",
                "alice.brown@example.com",
                "charlie.wilson@example.com",
                "diana.davis@example.com",
                "eve.miller@example.com",
                "frank.garcia@example.com",
                "grace.martinez@example.com",
                "henry.anderson@example.com",
            ],
            "Phone": [
                "555-0101",
                "555-0102",
                "555-0103",
                "555-0104",
                "555-0105",
                "555-0106",
                "555-0107",
                "555-0108",
                "555-0109",
                "555-0110",
            ],
            "Purchase Date": [datetime.now() - timedelta(days=i) for i in range(10)],
            "Amount": [round(random.uniform(25.0, 299.99), 2) for _ in range(10)],
        }

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def create_test_excel_file(self) -> bool:
        """Create a test Excel file with email data."""
        self.log("📊 Creating test Excel file with email data...")

        try:
            # Create DataFrame
            df = pd.DataFrame(self.test_data)

            # Save to Excel
            df.to_excel(self.test_excel_file, index=False)

            self.log(f"✅ Created test Excel file: {self.test_excel_file}")
            self.log(f"📊 Data: {len(df)} rows, {len(df.columns)} columns")
            self.log(f"📋 Columns: {', '.join(df.columns)}")
            self.log(
                f"📧 Emails: {len([email for email in df['Email'] if '@' in email])} valid emails"
            )

            return True

        except Exception as e:
            self.log(f"❌ Failed to create test Excel file: {e}", "ERROR")
            return False

    def test_sqlite_connection(self) -> bool:
        """Test SQLite database connection and schema."""
        self.log("🔌 Testing SQLite database connection...")

        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]

            self.log(f"📊 Found {len(tables)} tables: {', '.join(table_names)}")

            # Ensure schema_definitions table exists
            if "schema_definitions" not in table_names:
                self.log("❌ schema_definitions table not found", "ERROR")
                return False

            self.log("✅ SQLite connection test passed")
            return True

        except Exception as e:
            self.log(f"❌ SQLite connection test failed: {e}", "ERROR")
            return False

    def test_mongodb_connection(self) -> bool:
        """Test MongoDB Atlas connection."""
        self.log("🔌 Testing MongoDB Atlas connection...")

        try:
            # Test connection
            db = get_mongo_database()
            db.command("ping")

            self.log("✅ MongoDB Atlas connection test passed")
            return True

        except Exception as e:
            self.log(f"❌ MongoDB Atlas connection test failed: {e}", "ERROR")
            self.log(
                "💡 Make sure your MongoDB Atlas credentials are correct in .env file",
                "WARNING",
            )
            return False

    def create_schema_with_email_validation(self) -> Optional[str]:
        """Create SQLite schema with email duplication validation."""
        self.log("📋 Creating schema with email duplication validation...")

        try:
            # Step 1: Create schema ID
            schema_id = self.schema_manager.create_schema(self.test_schema_name, [])
            self.log(f"   ✅ Generated schema_id: {schema_id}")

            # Step 2: Create schema definition with email validation
            schema_def = SchemaDefinition(
                schema_id=schema_id,
                schema_name=self.test_schema_name,
                excel_column_names=list(self.test_data.keys()),
                normalized_attributes={
                    "First Name": "first_name",
                    "Last Name": "last_name",
                    "Email": "email",
                    "Phone": "phone",
                    "Purchase Date": "purchase_date",
                    "Amount": "amount",
                },
                suggested_indexes=[
                    {"field_names": ["email"], "index_type": "unique"},
                    {"field_names": ["phone"], "index_type": "unique"},
                ],
                duplicate_detection_columns=["email", "phone"],
                duplicate_strategy="skip",
                data_start_row=2,
                mongodb_collection_name=self.mongodb_collection_name,
                created_at=datetime.now(),
                last_used=datetime.now(),
                usage_count=0,
            )

            # Step 3: Save to SQLite database
            save_result = self.schema_manager.save_schema_definition(schema_def)
            if not save_result:
                self.log("❌ Failed to save schema to SQLite", "ERROR")
                return None

            self.log(f"✅ Schema created and saved with email validation")
            self.log(
                f"   🔍 Duplicate detection: {schema_def.duplicate_detection_columns}"
            )
            self.log(f"   🗄️ MongoDB collection: {schema_def.mongodb_collection_name}")

            return schema_id

        except Exception as e:
            self.log(f"❌ Schema creation failed: {e}", "ERROR")
            import traceback

            traceback.print_exc()
            return None

    def process_excel_to_mongodb(self, schema_id: str) -> bool:
        """Process Excel file and save to MongoDB collection 'test25'."""
        self.log("🔄 Processing Excel file to MongoDB collection 'test25'...")

        try:
            # Step 1: Validate Excel file
            if not self.excel_processor.validate_file(self.test_excel_file):
                self.log("❌ Excel file validation failed", "ERROR")
                return False

            # Step 2: Get file info
            file_info = self.excel_processor.get_file_info(self.test_excel_file)
            self.log(
                f"📊 File info: {file_info.total_rows} rows, {file_info.total_columns} columns"
            )

            # Step 3: Read Excel data
            df = pd.read_excel(self.test_excel_file)
            self.log(f"📋 Read {len(df)} rows from Excel")

            # Step 4: Create MongoDB collection
            collection = get_mongo_collection(self.mongodb_collection_name)
            self.log(f"🗄️ Using MongoDB collection: {self.mongodb_collection_name}")

            # Step 5: Process and insert data
            inserted_count = 0
            skipped_count = 0

            for index, row in df.iterrows():
                try:
                    # Convert row to document
                    document = {
                        "first_name": row["First Name"],
                        "last_name": row["Last Name"],
                        "email": row["Email"],
                        "phone": row["Phone"],
                        "purchase_date": row["Purchase Date"].isoformat()
                        if pd.notna(row["Purchase Date"])
                        else None,
                        "amount": float(row["Amount"])
                        if pd.notna(row["Amount"])
                        else 0.0,
                        "excel_row": index + 2,  # +2 because data starts at row 2
                        "imported_at": datetime.now(),
                    }

                    # Check for duplicates based on email
                    existing = collection.find_one({"email": document["email"]})
                    if existing:
                        self.log(f"⚠️ Skipping duplicate email: {document['email']}")
                        skipped_count += 1
                        continue

                    # Insert document
                    result = collection.insert_one(document)
                    inserted_count += 1
                    self.log(f"✅ Inserted row {index + 2}: {document['email']}")

                except Exception as e:
                    self.log(f"❌ Error processing row {index + 2}: {e}", "ERROR")
                    continue

            self.log(
                f"📊 Processing complete: {inserted_count} inserted, {skipped_count} skipped"
            )

            # Step 6: Create indexes
            collection.create_index("email", unique=True)
            collection.create_index("phone", unique=True)
            self.log("🔍 Created unique indexes on email and phone")

            return inserted_count > 0

        except Exception as e:
            self.log(f"❌ Excel to MongoDB processing failed: {e}", "ERROR")
            import traceback

            traceback.print_exc()
            return False

    def verify_mongodb_data(self) -> bool:
        """Verify data integrity in MongoDB collection 'test25'."""
        self.log("🔍 Verifying MongoDB data integrity...")

        try:
            collection = get_mongo_collection(self.mongodb_collection_name)

            # Count total documents
            total_docs = collection.count_documents({})
            self.log(f"📊 Total documents in collection: {total_docs}")

            if total_docs == 0:
                self.log("❌ No documents found in MongoDB collection", "ERROR")
                return False

            # Check for specific test data
            test_emails = [email for email in self.test_data["Email"]]
            found_emails = []

            for email in test_emails:
                doc = collection.find_one({"email": email})
                if doc:
                    found_emails.append(email)
                    self.log(f"✅ Found document for: {email}")
                else:
                    self.log(f"❌ Missing document for: {email}", "ERROR")

            # Check duplicate prevention
            duplicate_check = collection.find_one({"email": "john.doe@example.com"})
            if duplicate_check:
                # Try to insert duplicate
                try:
                    duplicate_doc = {
                        "first_name": "Duplicate",
                        "last_name": "User",
                        "email": "john.doe@example.com",
                        "phone": "555-9999",
                        "purchase_date": datetime.now().isoformat(),
                        "amount": 100.0,
                        "excel_row": 999,
                        "imported_at": datetime.now(),
                    }
                    collection.insert_one(duplicate_doc)
                    self.log(
                        "❌ Duplicate email was inserted - index not working", "ERROR"
                    )
                    return False
                except Exception as e:
                    if "duplicate key error" in str(e).lower():
                        self.log("✅ Duplicate prevention working correctly")
                    else:
                        self.log(
                            f"⚠️ Unexpected error on duplicate insert: {e}", "WARNING"
                        )

            self.log(
                f"✅ Data verification complete: {len(found_emails)}/{len(test_emails)} emails found"
            )
            return len(found_emails) == len(test_emails)

        except Exception as e:
            self.log(f"❌ MongoDB data verification failed: {e}", "ERROR")
            return False

    def verify_sqlite_schema(self, schema_id: str) -> bool:
        """Verify schema was saved correctly in SQLite."""
        self.log("🔍 Verifying SQLite schema...")

        try:
            conn = get_sqlite_connection()
            cursor = conn.cursor()

            # Check schema was saved
            cursor.execute(
                """
                SELECT schema_id, schema_name, mongodb_collection_name, duplicate_detection_columns
                FROM schema_definitions 
                WHERE schema_id = ?
            """,
                (schema_id,),
            )

            row = cursor.fetchone()
            if row:
                self.log(f"✅ Schema found in SQLite:")
                self.log(f"   🆔 ID: {row[0]}")
                self.log(f"   📝 Name: {row[1]}")
                self.log(f"   🗄️ Collection: {row[2]}")
                self.log(f"   🔍 Duplicate columns: {row[3]}")
                return True
            else:
                self.log("❌ Schema not found in SQLite", "ERROR")
                return False

        except Exception as e:
            self.log(f"❌ SQLite schema verification failed: {e}", "ERROR")
            return False

    def cleanup_test_data(self):
        """Clean up test data from both databases."""
        self.log("🧹 Cleaning up test data...")

        try:
            # Clean up SQLite
            conn = get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM schema_definitions WHERE schema_name = ?",
                (self.test_schema_name,),
            )
            deleted_count = cursor.rowcount
            conn.commit()
            self.log(f"✅ Deleted {deleted_count} schema(s) from SQLite")

            # Clean up MongoDB
            collection = get_mongo_collection(self.mongodb_collection_name)
            result = collection.delete_many({})
            self.log(
                f"✅ Deleted {result.deleted_count} documents from MongoDB collection '{self.mongodb_collection_name}'"
            )

            # Clean up Excel file
            if self.test_excel_file.exists():
                self.test_excel_file.unlink()
                self.log("✅ Deleted test Excel file")

        except Exception as e:
            self.log(f"❌ Cleanup failed: {e}", "ERROR")

    def run_all_tests(self) -> bool:
        """Run all MongoDB E2E tests."""
        self.log("🚀 Starting MongoDB E2E Test Suite for MoneyFlowV2")
        self.log("=" * 70)

        tests = [
            ("Create Test Excel File", self.create_test_excel_file),
            ("SQLite Connection", self.test_sqlite_connection),
            ("MongoDB Atlas Connection", self.test_mongodb_connection),
        ]

        # Run initial tests
        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            self.log(f"\n🧪 Running: {test_name}")
            self.log("-" * 50)

            if test_func():
                self.log(f"✅ {test_name} PASSED")
                passed += 1
            else:
                self.log(f"❌ {test_name} FAILED")
                if test_name == "MongoDB Atlas Connection":
                    self.log("💡 Cannot proceed without MongoDB connection", "ERROR")
                    return False

        # If initial tests pass, run workflow tests
        if passed == total:
            self.log("\n🔄 Running MongoDB workflow tests...")

            # Create schema
            schema_id = self.create_schema_with_email_validation()
            if not schema_id:
                self.log("❌ Schema creation failed - cannot proceed", "ERROR")
                return False

            # Process Excel to MongoDB
            if not self.process_excel_to_mongodb(schema_id):
                self.log("❌ Excel to MongoDB processing failed", "ERROR")
                return False

            # Verify data
            if not self.verify_mongodb_data():
                self.log("❌ MongoDB data verification failed", "ERROR")
                return False

            if not self.verify_sqlite_schema(schema_id):
                self.log("❌ SQLite schema verification failed", "ERROR")
                return False

            self.log("✅ All MongoDB workflow tests passed!")
            return True

        return False


def main():
    """Main MongoDB E2E test function."""
    tester = MongoDBE2ETester()

    try:
        success = tester.run_all_tests()

        # Always cleanup
        tester.cleanup_test_data()

        if success:
            print("\n🎉 MongoDB E2E Test Suite PASSED!")
            print("✅ Excel file processed successfully")
            print("✅ Data saved to MongoDB Atlas collection 'test25'")
            print("✅ Email duplication validation working")
            print("✅ Both SQLite and MongoDB data integrity verified")
            print("\n🔍 Check your MongoDB Atlas dashboard to see collection 'test25'")
        else:
            print("\n❌ MongoDB E2E Test Suite FAILED!")
            print("Check the logs above for details")

        return 0 if success else 1

    except Exception as e:
        print(f"❌ MongoDB E2E test suite failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
