#!/usr/bin/env python3
"""
MongoDB E2E Test Runner

This script runs the MongoDB end-to-end test to verify the complete
Excel-to-MongoDB workflow with email duplication validation.
"""

import sys
from pathlib import Path


def main():
    """Run the MongoDB E2E test."""
    print("🚀 MongoDB E2E Test Runner")
    print("=" * 50)

    # Add tests directory to path
    tests_dir = Path(__file__).parent.parent / "tests"
    sys.path.insert(0, str(tests_dir))

    try:
        # Import and run the test
        from e2e.test_mongodb_workflow import main as run_test

        return run_test()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the project root")
        print("   directory")
        return 1
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
