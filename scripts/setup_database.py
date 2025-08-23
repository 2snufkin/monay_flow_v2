#!/usr/bin/env python3
"""
Database Setup Script

Sets up the SQLite database schema and tests MongoDB connection.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Setup databases and test connections."""
    print("🗄️  Setting up MoneyFlow Database Connections")
    print("=" * 50)
    
    try:
        from config.database_config import DatabaseManager
        from config.settings import validate_settings
        
        # Validate settings first
        print("🔧 Validating application settings...")
        if not validate_settings():
            print("❌ Settings validation failed. Check your .env file.")
            return 1
        print("✅ Settings validation passed")
        
        # Initialize database manager
        print("\n🔌 Initializing database connections...")
        db_manager = DatabaseManager()
        
        if db_manager.initialize():
            print("✅ Database initialization successful!")
            print("\n📊 Database Status:")
            print("  • SQLite: Ready for schema storage and UI state")
            print("  • MongoDB: Connected and ready for Excel data storage (database: excel_imports)")
            print("  • Architecture: SQLite (metadata) + MongoDB (data)")
        else:
            print("❌ Database initialization failed")
            print("Check your MongoDB connection settings in .env file")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've installed all dependencies:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
