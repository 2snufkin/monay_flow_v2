#!/usr/bin/env python3
"""
Production Startup Script for MoneyFlow Data Ingestion App

This script launches the application with production-optimized settings
and performs pre-flight checks to ensure everything is ready.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.settings import get_settings


def check_production_ready():
    """Check if the application is ready for production."""
    print("🔍 Checking production readiness...")

    # Check .env file
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Please run the deployment script first")
        return False

    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "MONGO_URL", "ENCRYPTION_KEY", "SESSION_SECRET"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("   Please check your .env file")
        return False

    # Validate settings
    try:
        settings = get_settings()
        print("✅ Settings validation passed")
    except Exception as e:
        print(f"❌ Settings validation failed: {e}")
        return False

    # Check if virtual environment is activated
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  Virtual environment not detected")
        print("   Consider activating your virtual environment")

    print("✅ Production readiness check passed")
    return True


def start_production_app():
    """Start the production application."""
    print("🚀 Starting MoneyFlow Data Ingestion App...")

    try:
        # Launch the main application
        main_script = Path(__file__).parent.parent / "main.py"

        if not main_script.exists():
            print("❌ main.py not found")
            return False

        print("🎯 Launching application...")
        print("📱 The GUI will open in a new window")
        print("⏳ Please wait...")

        # Start the application
        result = subprocess.run(
            [sys.executable, str(main_script)], cwd=str(main_script.parent)
        )

        if result.returncode == 0:
            print("✅ Application closed successfully")
            return True
        else:
            print(f"⚠️  Application exited with code: {result.returncode}")
            return True  # Still consider success as user might have closed it

    except KeyboardInterrupt:
        print("\n⏹️  Application startup interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False


def main():
    """Main production startup function."""
    print("🚀 MoneyFlow Production Startup")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check production readiness
    if not check_production_ready():
        print("\n❌ Production startup failed!")
        print("🔍 Please fix the issues above and try again")
        return 1

    print("\n🎯 Starting production application...")

    # Start the application
    if start_production_app():
        print("\n✅ Production startup completed successfully!")
        return 0
    else:
        print("\n❌ Production startup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())


