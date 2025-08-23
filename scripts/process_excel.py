#!/usr/bin/env python3
"""
Excel Processing Script

Demonstrates the app's Excel processing capabilities.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Also add the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Process Excel files and demonstrate functionality."""
    print("📊 MoneyFlow Excel Processing Demo")
    print("=" * 50)
    
    try:
        from core.excel_processor import ExcelProcessor
        from core.ai_processor import AISchemaProcessor
        from core.schema_manager import SchemaManager
        from config.settings import validate_settings
        
        # Validate settings
        print("🔧 Validating settings...")
        if not validate_settings():
            print("❌ Settings validation failed")
            return 1
        print("✅ Settings validation passed")
        
        # Initialize components
        print("\n🚀 Initializing components...")
        excel_processor = ExcelProcessor()
        ai_processor = AISchemaProcessor()
        schema_manager = SchemaManager()
        
        # Check for Excel files
        excel_files = list(Path(".").glob("*.xls*"))
        if not excel_files:
            print("❌ No Excel files found in current directory")
            print("Please place an Excel file in the project root directory")
            return 1
        
        print(f"📁 Found {len(excel_files)} Excel file(s):")
        for file in excel_files:
            print(f"  • {file.name}")
        
        # Process the first Excel file
        excel_file = excel_files[0]
        print(f"\n🔍 Processing: {excel_file.name}")
        
        # Read Excel file
        print("📖 Reading Excel file...")
        # Use start_row=2 (assuming first row is headers, data starts from row 2)
        df_iterator = excel_processor.read_excel_file_stream(str(excel_file), start_row=2)
        # Get first batch to show data
        first_batch = next(df_iterator)
        print(f"✅ Loaded {len(first_batch)} rows from first batch")
        
        # Get column names
        column_names = excel_processor.get_excel_column_names(str(excel_file))
        print(f"📋 Columns: {', '.join(column_names)}")
        
        # Preview data
        print("\n👀 Data Preview (first 3 rows):")
        preview = excel_processor.preview_excel_data(str(excel_file), start_row=2, limit=3)
        print(preview)
        
        # Calculate file hash
        file_hash = excel_processor.calculate_file_hash(str(excel_file))
        print(f"🔐 File hash: {file_hash[:16]}...")
        
        print("\n🎯 Excel processing successful!")
        print("The app is ready to:")
        print("• Create schemas from column names")
        print("• Use AI to normalize field names")
        print("• Store data in MongoDB")
        print("• Handle duplicate detection")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
