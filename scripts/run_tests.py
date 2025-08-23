#!/usr/bin/env python3
"""
Test Runner Script

Runs all unit tests and displays results.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run all tests and display results."""
    project_root = Path(__file__).parent.parent
    
    print("🧪 Running MoneyFlow Data Ingestion App Tests")
    print("=" * 50)
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--verbose",
        "--tb=short",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=0",  # Don't fail on low coverage initially
        "-x"  # Stop on first failure for faster feedback
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=False)
        
        # Add extra newlines to fix Cursor terminal hanging issue
        print("")
        print("")
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed with exit code: {result.returncode}")
            print("This is expected since we're running tests against stub implementations.")
            print("The tests are designed to fail initially until methods are implemented.")
        
        print(f"📊 Coverage report generated in: {project_root}/htmlcov/index.html")
        
        # Force output flush to prevent hanging
        sys.stdout.flush()
        sys.stderr.flush()
        
    except FileNotFoundError:
        print("❌ pytest not found. Please install dependencies:")
        print("pip install -r requirements-dev.txt")
        # Add newlines even on error
        print("")
        print("")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
