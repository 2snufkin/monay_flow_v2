#!/usr/bin/env python3
"""
MoneyFlow Data Ingestion App - Main Entry Point

This is the main entry point for the MoneyFlow data ingestion application.
It initializes the UI and starts the application.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """
    Main entry point for the application.
    """
    try:
        # Setup logging first
        from config.logging_config import setup_development_logging, get_logger
        setup_development_logging()
        logger = get_logger(__name__)
        
        logger.info("🚀 MoneyFlow Data Ingestion App Starting")
        logger.info("=" * 50)
        
        # Test core functionality
        from core.schema_manager import SchemaManager
        from core.excel_processor import ExcelProcessor
        from core.ai_processor import AISchemaProcessor
        from core.mongo_collection_manager import MongoCollectionManager
        from core.data_ingestion_engine import DataIngestionEngine
        from config.settings import get_settings
        
        logger.info("All core modules imported successfully")
        
        # Validate settings
        settings = get_settings()
        logger.info("Settings validation passed")
        
        # Initialize core components
        schema_manager = SchemaManager()
        excel_processor = ExcelProcessor()
        ai_processor = AISchemaProcessor()
        mongo_manager = MongoCollectionManager()
        ingestion_engine = DataIngestionEngine()
        
        logger.info("All core components initialized")
        
        # Show available schemas
        schemas = schema_manager.get_all_schemas()
        logger.info(f"Found {len(schemas)} existing schemas")
        
        logger.info("🎯 Application ready for use!")
        logger.info("Launching GUI...")
        
        # Launch the GUI
        from ui.main_window import ModernMainWindow
        app = ModernMainWindow()
        app.run()
        
        return 0
        
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Error starting application: {e}")
            logger.debug("Stack trace:", exc_info=True)
        else:
            print(f"❌ Error starting application: {e}")
            print("Please check your dependencies and configuration.")
        return 1


if __name__ == "__main__":
    main()
