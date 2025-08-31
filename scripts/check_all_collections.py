#!/usr/bin/env python3
"""
Check All MongoDB Collections Script

This script lists all collections in the MongoDB database to see what's been created.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def check_all_collections():
    """Check all collections in MongoDB."""
    print("🔍 Checking All MongoDB Collections...")
    print("=" * 50)
    
    try:
        from pymongo import MongoClient
        import os
        
        mongo_url = os.getenv('MONGO_URL')
        if not mongo_url:
            print("❌ No MongoDB URL found in environment!")
            return
        
        print(f"📡 Connecting to MongoDB...")
        client = MongoClient(mongo_url)
        
        # Get database name from URL or use default
        db_name = "excel_imports"  # Default from env.example
        if "/" in mongo_url:
            db_name = mongo_url.split("/")[-1].split("?")[0]
        
        print(f"🗄️  Database: {db_name}")
        db = client[db_name]
        
        # List all collections
        collections = db.list_collection_names()
        
        if not collections:
            print("📭 No collections found in database")
        else:
            print(f"📚 Found {len(collections)} collections:")
            for i, coll_name in enumerate(collections, 1):
                print(f"  {i}. {coll_name}")
                
                # Get document count for each collection
                try:
                    count = db[coll_name].count_documents({})
                    print(f"     📊 Documents: {count}")
                    
                    # Show sample document structure if any exist
                    if count > 0:
                        sample = db[coll_name].find_one()
                        if sample:
                            print(f"     📋 Sample fields: {list(sample.keys())}")
                except Exception as e:
                    print(f"     ⚠️  Error checking collection: {e}")
                print()
        
        client.close()
        print("✅ MongoDB connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the collection check."""
    print("🚀 MongoDB Collections Checker")
    print("=" * 60)
    
    check_all_collections()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()


