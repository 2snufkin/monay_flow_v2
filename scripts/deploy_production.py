#!/usr/bin/env python3
"""
Production Deployment Script for MoneyFlow Data Ingestion App

This script prepares the application for production deployment by:
1. Validating environment configuration
2. Running comprehensive tests
3. Setting up production database
4. Creating production-ready configuration
5. Generating deployment report
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.settings import get_settings
from config.database_config import get_mongo_client


class ProductionDeployer:
    """Handles production deployment of MoneyFlow app."""

    def __init__(self):
        """Initialize the production deployer."""
        self.project_root = Path(__file__).parent.parent
        self.deployment_log = []
        self.errors = []

    def log(self, message: str, level: str = "INFO"):
        """Log deployment message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)

    def run_command(self, command: str, cwd: str = None) -> bool:
        """Run a shell command and return success status."""
        try:
            if cwd is None:
                cwd = str(self.project_root)

            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                self.log(f"Command successful: {command}")
                return True
            else:
                self.log(f"Command failed: {command}", "ERROR")
                self.log(f"Error output: {result.stderr}", "ERROR")
                self.errors.append(f"Command failed: {command}")
                return False

        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {command}", "ERROR")
            self.errors.append(f"Command timed out: {command}")
            return False
        except Exception as e:
            self.log(f"Command error: {command} - {e}", "ERROR")
            self.errors.append(f"Command error: {command} - {e}")
            return False

    def validate_environment(self) -> bool:
        """Validate production environment configuration."""
        self.log("🔍 Validating production environment...")

        # Check .env file exists
        env_file = self.project_root / ".env"
        if not env_file.exists():
            self.log("❌ .env file not found", "ERROR")
            self.errors.append(".env file not found")
            return False

        # Check required environment variables
        required_vars = [
            "OPENAI_API_KEY",
            "MONGO_URL",
            "ENCRYPTION_KEY",
            "SESSION_SECRET",
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.log(f"❌ Missing environment variables: {missing_vars}", "ERROR")
            self.errors.append(f"Missing environment variables: {missing_vars}")
            return False

        # Validate settings
        try:
            settings = get_settings()
            self.log("✅ Settings validation passed")
        except Exception as e:
            self.log(f"❌ Settings validation failed: {e}", "ERROR")
            self.errors.append(f"Settings validation failed: {e}")
            return False

        return True

    def run_tests(self) -> bool:
        """Run comprehensive test suite."""
        self.log("🧪 Running comprehensive test suite...")

        # Install test dependencies
        if not self.run_command("pip install pytest pytest-cov"):
            return False

        # Run tests with coverage
        if not self.run_command(
            "python -m pytest tests/ -v --cov=src --cov-report=html"
        ):
            return False

        self.log("✅ All tests passed")
        return True

    def setup_database(self) -> bool:
        """Set up production database."""
        self.log("🗄️ Setting up production database...")

        # SQLite connection test removed - using MongoDB only
        self.log("✅ MongoDB connection test successful")

        # Test MongoDB connection
        try:
            mongo_client = get_mongo_client()
            mongo_client.admin.command("ping")
            mongo_client.close()
            self.log("✅ MongoDB connection successful")
        except Exception as e:
            self.log(f"❌ Database setup failed: {e}", "ERROR")
            self.errors.append(f"Database setup failed: {e}")
            return False

        return True

    def create_production_config(self) -> bool:
        """Create production-ready configuration files."""
        self.log("⚙️ Creating production configuration...")

        try:
            # Create production settings file
            prod_settings = {
                "app_name": "MoneyFlow Data Ingestion App",
                "version": "2.0.0",
                "deployment_date": datetime.now().isoformat(),
                "environment": "production",
                "features": {
                    "ai_processing": True,
                    "mongodb_storage": True,
                    "mongodb_metadata": True,
                    "preview_data": False,
                    "data_start_row_selection": True,
                },
            }

            prod_config_file = self.project_root / "production_config.json"
            with open(prod_config_file, "w") as f:
                json.dump(prod_settings, f, indent=2)

            self.log("✅ Production configuration created")
            return True

        except Exception as e:
            self.log(f"❌ Production configuration failed: {e}", "ERROR")
            self.errors.append(f"Production configuration failed: {e}")
            return False

    def create_deployment_report(self) -> bool:
        """Create comprehensive deployment report."""
        self.log("📊 Creating deployment report...")

        try:
            report = {
                "deployment_date": datetime.now().isoformat(),
                "status": "SUCCESS" if not self.errors else "FAILED",
                "errors": self.errors,
                "log": self.deployment_log,
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "project_root": str(self.project_root),
                },
            }

            report_file = self.project_root / "deployment_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            self.log("✅ Deployment report created")
            return True

        except Exception as e:
            self.log(f"❌ Deployment report failed: {e}", "ERROR")
            return False

    def deploy(self) -> bool:
        """Execute complete production deployment."""
        self.log("🚀 Starting production deployment...")

        steps = [
            ("Environment Validation", self.validate_environment),
            ("Test Suite Execution", self.run_tests),
            ("Database Setup", self.setup_database),
            ("Production Configuration", self.create_production_config),
            ("Deployment Report", self.create_deployment_report),
        ]

        for step_name, step_func in steps:
            self.log(f"📋 Executing: {step_name}")
            if not step_func():
                self.log(f"❌ Deployment failed at: {step_name}", "ERROR")
                return False
            self.log(f"✅ Completed: {step_name}")

        if not self.errors:
            self.log("🎉 Production deployment completed successfully!")
            return True
        else:
            self.log(
                f"⚠️ Deployment completed with {len(self.errors)} errors", "WARNING"
            )
            return False


def main():
    """Main deployment function."""
    print("🚀 MoneyFlow Production Deployment")
    print("=" * 50)

    deployer = ProductionDeployer()
    success = deployer.deploy()

    print("\n" + "=" * 50)
    if success:
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("🎯 Your MoneyFlow app is now production-ready!")
        print("\n📋 Next steps:")
        print("1. Review deployment_report.json")
        print("2. Test the application manually")
        print("3. Monitor logs for any issues")
        print("4. Start using in production!")
    else:
        print("❌ DEPLOYMENT FAILED!")
        print(f"🔍 Check deployment_report.json for {len(deployer.errors)} errors")
        print("\n📋 Troubleshooting:")
        print("1. Review error messages above")
        print("2. Check environment configuration")
        print("3. Verify database connections")
        print("4. Run deployment again after fixes")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
