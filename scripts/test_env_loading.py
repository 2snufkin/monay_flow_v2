#!/usr/bin/env python3
"""
Test Environment Variable Loading

This script tests if the .env file is being loaded correctly.
"""

import os
from pathlib import Path


def test_env_loading():
    """Test if environment variables are loaded from .env file."""
    print("🔍 Testing environment variable loading...")

    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ .env file found: {env_file}")
        print(f"📏 File size: {env_file.stat().st_size} bytes")
    else:
        print("❌ .env file not found")
        return False

    # Check key environment variables
    key_vars = [
        "MONGO_URL",
        "MONGO_DATABASE",
        "OPENAI_API_KEY",
        "ENCRYPTION_KEY",
        "SESSION_SECRET",
    ]

    print("\n📋 Environment Variables:")
    for var in key_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "password" in var.lower() or "key" in var.lower():
                masked_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                masked_value = value
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: Not set")

    # Check if python-dotenv is working
    try:
        from dotenv import load_dotenv

        print("\n🔌 Testing python-dotenv...")
        load_dotenv()

        print("\n📋 After load_dotenv():")
        for var in key_vars:
            value = os.getenv(var)
            if value:
                if "password" in var.lower() or "key" in var.lower():
                    masked_value = value[:10] + "..." if len(value) > 10 else "***"
                else:
                    masked_value = value
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ❌ {var}: Not set")

        return True

    except ImportError as e:
        print(f"❌ python-dotenv import failed:")
        print(f"   {e}")
        return False


if __name__ == "__main__":
    success = test_env_loading()
    exit(0 if success else 1)
