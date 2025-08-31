"""
Pytest configuration and shared fixtures.
"""

import pytest
import tempfile

# SQLite import removed
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Generator, Dict, Any

import pandas as pd
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


# SQLite database fixture removed - using MongoDB only


@pytest.fixture
def mock_mongo_client() -> Mock:
    """Create a mock MongoDB client."""
    mock_client = Mock(spec=MongoClient)
    mock_db = Mock(spec=Database)
    mock_collection = Mock(spec=Collection)

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    # Mock common operations
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value = Mock(inserted_id="test_id")
    mock_collection.bulk_write.return_value = Mock(inserted_count=0, modified_count=0)

    return mock_client


@pytest.fixture
def sample_excel_data() -> Dict[str, Any]:
    """Sample Excel data for testing."""
    return {
        "columns": ["Purchase Date", "Customer Email", "Product Name", "Amount"],
        "data": [
            ["2025-01-20", "john@email.com", "Laptop", "999.99"],
            ["2025-01-21", "jane@email.com", "Mouse", "29.99"],
            ["2025-01-22", "bob@email.com", "Keyboard", "79.99"],
        ],
    }


@pytest.fixture
def sample_excel_file(temp_dir: Path, sample_excel_data: Dict[str, Any]) -> Path:
    """Create a sample Excel file for testing."""
    file_path = temp_dir / "test_data.xlsx"

    df = pd.DataFrame(sample_excel_data["data"], columns=sample_excel_data["columns"])
    df.to_excel(file_path, index=False)

    return file_path


@pytest.fixture
def sample_schema_definition() -> Dict[str, Any]:
    """Sample schema definition for testing."""
    return {
        "schema_id": "test_schema_123",
        "schema_name": "Test Customer Data",
        "original_columns": [
            "Purchase Date",
            "Customer Email",
            "Product Name",
            "Amount",
        ],
        "normalized_attributes": {
            "Purchase Date": {
                "field_name": "purchase_date",
                "data_type": "Date",
                "description": "Date of purchase",
                "is_required": True,
            },
            "Customer Email": {
                "field_name": "customer_email",
                "data_type": "String",
                "description": "Customer email address",
                "is_required": True,
            },
            "Product Name": {
                "field_name": "product_name",
                "data_type": "String",
                "description": "Name of the product",
                "is_required": True,
            },
            "Amount": {
                "field_name": "amount",
                "data_type": "Number",
                "description": "Purchase amount",
                "is_required": True,
            },
        },
        "suggested_indexes": [
            {
                "field": "customer_email",
                "type": "ascending",
                "reason": "Frequently queried field",
            },
            {
                "field": "purchase_date",
                "type": "ascending",
                "reason": "Time-based queries",
            },
        ],
        "duplicate_detection_columns": ["customer_email", "purchase_date"],
        "duplicate_strategy": "skip",
        "data_start_row": 2,
        "mongodb_collection_name": "test_customer_data",
        "usage_count": 0,
    }


@pytest.fixture
def mock_openai_response() -> Dict[str, Any]:
    """Mock OpenAI API response for testing."""
    return {
        "normalized_attributes": {
            "Purchase Date": {
                "field_name": "purchase_date",
                "data_type": "Date",
                "description": "Date of purchase transaction",
            },
            "Customer Email": {
                "field_name": "customer_email",
                "data_type": "String",
                "description": "Customer's email address",
            },
            "Product Name": {
                "field_name": "product_name",
                "data_type": "String",
                "description": "Name of purchased product",
            },
            "Amount": {
                "field_name": "amount",
                "data_type": "Number",
                "description": "Purchase amount in currency",
            },
        },
        "suggested_indexes": [
            {
                "field": "customer_email",
                "type": "unique",
                "reason": "Email should be unique identifier",
            },
            {
                "field": "purchase_date",
                "type": "ascending",
                "reason": "Temporal queries optimization",
            },
        ],
        "duplicate_detection": {
            "primary_keys": ["customer_email", "purchase_date"],
            "reasoning": "Email and date combination should be unique per customer",
        },
        "collection_name": "customer_purchases",
    }


@pytest.fixture
def mock_settings():
    """Mock application settings for testing."""
    with patch("src.config.settings.get_settings") as mock_get_settings:
        mock_settings_obj = Mock()
        # SQLite settings removed - using MongoDB only
        mock_settings_obj.database.mongo_url = "mongodb://localhost:27017"
        mock_settings_obj.database.mongo_database = "test_db"
        mock_settings_obj.ai.openai_api_key = "test_key"
        mock_settings_obj.ai.openai_model = "gpt-4"
        mock_settings_obj.processing.batch_size = 100
        mock_get_settings.return_value = mock_settings_obj
        yield mock_settings_obj


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
pytest.mark.ai = pytest.mark.ai
pytest.mark.database = pytest.mark.database
