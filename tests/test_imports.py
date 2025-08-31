#!/usr/bin/env python3
"""
Test script to verify core module imports work correctly.
"""

import sys
import os
from pathlib import Path

def test_core_imports():
    """Test that all core modules can be imported successfully."""
    print("🔍 Testing core module imports...")
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    
    print("📁 Testing imports one by one...")
    
    try:
        print("1️⃣ Testing database_config import...")
        from config.database_config import get_sqlite_connection
        print("   ✅ database_config imported successfully")
    except Exception as e:
        print(f"   ❌ database_config import failed: {e}")
        return False
    
    try:
        print("2️⃣ Testing schema_definition import...")
        # Import test - just checking if it works
        import models.schema_definition
        print("   ✅ schema_definition imported successfully")
    except Exception as e:
        print(f"   ❌ schema_definition import failed: {e}")
        return False
    
    try:
        print("3️⃣ Testing schema_manager import...")
        # Import test - just checking if it works
        import core.schema_manager
        print("   ✅ schema_manager imported successfully")
    except Exception as e:
        print(f"   ❌ schema_manager import failed: {e}")
        return False
    
    print("🎯 All core imports successful!")
    return True

if __name__ == "__main__":
    success = test_core_imports()
    if success:
        print("✅ Import test passed!")
    else:
        print("❌ Import test failed!")
        sys.exit(1)
