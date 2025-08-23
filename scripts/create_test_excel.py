#!/usr/bin/env python3
"""
Create Test Excel File

Creates a sample Excel file for testing the app.
"""

import pandas as pd
from datetime import datetime, timedelta
import random


def main():
    """Create a test Excel file with sample data."""
    print("📊 Creating Test Excel File")
    print("=" * 50)
    
    try:
        # Create sample data
        data = {
            'Purchase Date': [datetime.now() - timedelta(days=i) for i in range(10)],
            'Item Name': [f'Product {i+1}' for i in range(10)],
            'Category': random.choices(['Electronics', 'Clothing', 'Food', 'Books'], k=10),
            'Amount': [round(random.uniform(10.0, 500.0), 2) for _ in range(10)],
            'Payment Method': random.choices(['Credit Card', 'Cash', 'PayPal'], k=10),
            'Store': random.choices(['Amazon', 'Walmart', 'Target', 'Local Shop'], k=10),
            'Customer ID': [f'CUST_{i+1:03d}' for i in range(10)],
            'Email': [f'customer{i+1}@example.com' for i in range(10)]
        }
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to Excel
        filename = 'test_data.xlsx'
        df.to_excel(filename, index=False)
        
        print(f"✅ Created test Excel file: {filename}")
        print(f"📊 Data: {len(df)} rows, {len(df.columns)} columns")
        print(f"📋 Columns: {', '.join(df.columns)}")
        print("\n👀 Sample data:")
        print(df.head(3).to_string(index=False))
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    main()

