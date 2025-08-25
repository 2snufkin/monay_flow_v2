#!/usr/bin/env python3
"""
Simple MongoDB Connection Test

This script tests the MongoDB Atlas connection to verify credentials.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_mongodb_connection():
    """Test MongoDB Atlas connection."""
    try:
        from config.database_config import get_mongo_database

        print("🔌 Testing MongoDB Atlas connection...")

        # Test connection
        db = get_mongo_database()
        db.command("ping")

        print("✅ MongoDB Atlas connection successful!")
        print(f"📊 Database name: {db.name}")

        # List collections
        collections = db.list_collection_names()
        print(f"📋 Collections: {collections}")

        return True

    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {e}")
        print("\n💡 Please check:")
        print("   1. Your .env file has correct MongoDB credentials")
        print("   2. MongoDB Atlas is accessible from your network")
        print("   3. Username and password are correct")
        return False


if __name__ == "__main__":
    success = test_mongodb_connection()
    exit(0 if success else 1)
