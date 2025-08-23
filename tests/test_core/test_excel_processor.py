"""
Unit tests for ExcelProcessor class.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any, Iterator

from src.core.excel_processor import ExcelProcessor
from src.models.validation_result import ValidationResult


@pytest.mark.unit
class TestExcelProcessor:
    """Test cases for ExcelProcessor class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.excel_processor = ExcelProcessor()
    
    def test_read_excel_file_stream_success(self, sample_excel_file):
        """Test successful reading of Excel file as stream."""
        batches = list(self.excel_processor.read_excel_file_stream(
            str(sample_excel_file), 
            start_row=2,  # Skip header row
            batch_size=2
        ))
        
        assert len(batches) > 0
        # First batch should contain dictionaries with column names as keys
        first_batch = batches[0]
        assert isinstance(first_batch, list)
        assert len(first_batch) > 0
        assert isinstance(first_batch[0], dict)
        assert "Purchase Date" in first_batch[0]
    
    def test_read_excel_file_stream_nonexistent_file(self):
        """Test reading non-existent Excel file."""
        with pytest.raises(FileNotFoundError):
            list(self.excel_processor.read_excel_file_stream(
                "nonexistent.xlsx",
                start_row=2
            ))
    
    def test_read_excel_file_stream_invalid_start_row(self, sample_excel_file):
        """Test reading with invalid start row."""
        with pytest.raises(ValueError):
            list(self.excel_processor.read_excel_file_stream(
                str(sample_excel_file),
                start_row=0  # Invalid row number
            ))
    
    def test_validate_excel_structure_matching_columns(self, sample_excel_file):
        """Test validation with matching column structure."""
        expected_columns = ["Purchase Date", "Customer Email", "Product Name", "Amount"]
        
        result = self.excel_processor.validate_excel_structure(
            str(sample_excel_file),
            expected_columns,
            header_row=1
        )
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_excel_structure_missing_columns(self, sample_excel_file):
        """Test validation with missing columns."""
        expected_columns = ["Purchase Date", "Customer Email", "Product Name", "Amount", "Missing Column"]
        
        result = self.excel_processor.validate_excel_structure(
            str(sample_excel_file),
            expected_columns,
            header_row=1
        )
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Missing Column" in str(result.errors)
    
    def test_validate_excel_structure_extra_columns(self, sample_excel_file):
        """Test validation with extra columns in Excel."""
        expected_columns = ["Purchase Date", "Customer Email"]  # Missing some columns
        
        result = self.excel_processor.validate_excel_structure(
            str(sample_excel_file),
            expected_columns,
            header_row=1
        )
        
        assert isinstance(result, ValidationResult)
        # Extra columns should produce warnings, not errors
        assert len(result.warnings) > 0
    
    def test_preview_excel_data_success(self, sample_excel_file):
        """Test successful preview of Excel data."""
        result = self.excel_processor.preview_excel_data(
            str(sample_excel_file),
            start_row=2,
            limit=2
        )
        
        assert isinstance(result, list)
        assert len(result) <= 2  # Respects limit
        assert all(isinstance(row, dict) for row in result)
        if result:
            assert "Purchase Date" in result[0]
    
    def test_preview_excel_data_large_limit(self, sample_excel_file):
        """Test preview with limit larger than available data."""
        result = self.excel_processor.preview_excel_data(
            str(sample_excel_file),
            start_row=2,
            limit=100  # More than available rows
        )
        
        assert isinstance(result, list)
        # Should return all available rows, not fail
        assert len(result) <= 100
    
    def test_get_excel_column_names_success(self, sample_excel_file):
        """Test successful extraction of column names."""
        result = self.excel_processor.get_excel_column_names(
            str(sample_excel_file),
            header_row=1
        )
        
        assert isinstance(result, list)
        assert len(result) == 4
        assert "Purchase Date" in result
        assert "Customer Email" in result
        assert "Product Name" in result
        assert "Amount" in result
    
    def test_get_excel_column_names_invalid_header_row(self, sample_excel_file):
        """Test extraction with invalid header row."""
        with pytest.raises(ValueError):
            self.excel_processor.get_excel_column_names(
                str(sample_excel_file),
                header_row=0  # Invalid row
            )
    
    def test_get_excel_row_count_success(self, sample_excel_file):
        """Test successful row count calculation."""
        result = self.excel_processor.get_excel_row_count(str(sample_excel_file))
        
        assert isinstance(result, int)
        assert result > 0  # Should include header + data rows
    
    def test_get_excel_row_count_nonexistent_file(self):
        """Test row count with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.excel_processor.get_excel_row_count("nonexistent.xlsx")
    
    def test_calculate_file_hash_success(self, sample_excel_file):
        """Test successful file hash calculation."""
        result = self.excel_processor.calculate_file_hash(str(sample_excel_file))
        
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hash length
        
        # Hash should be consistent
        result2 = self.excel_processor.calculate_file_hash(str(sample_excel_file))
        assert result == result2
    
    def test_calculate_file_hash_nonexistent_file(self):
        """Test file hash with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.excel_processor.calculate_file_hash("nonexistent.xlsx")
    
    def test_calculate_file_hash_different_files(self, temp_dir):
        """Test that different files produce different hashes."""
        # Create two different Excel files
        file1 = temp_dir / "file1.xlsx"
        file2 = temp_dir / "file2.xlsx"
        
        df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = pd.DataFrame({"A": [5, 6], "B": [7, 8]})
        
        df1.to_excel(file1, index=False)
        df2.to_excel(file2, index=False)
        
        hash1 = self.excel_processor.calculate_file_hash(str(file1))
        hash2 = self.excel_processor.calculate_file_hash(str(file2))
        
        assert hash1 != hash2
    
    def test_excel_processor_initialization(self):
        """Test ExcelProcessor initialization."""
        processor = ExcelProcessor()
        assert processor is not None
    
    def test_read_excel_file_stream_batch_size(self, sample_excel_file):
        """Test that batching works correctly."""
        batch_size = 1
        batches = list(self.excel_processor.read_excel_file_stream(
            str(sample_excel_file),
            start_row=2,
            batch_size=batch_size
        ))
        
        # Each batch should have at most batch_size rows
        for batch in batches:
            assert len(batch) <= batch_size
    
    @patch('pandas.read_excel')
    def test_read_excel_file_stream_handles_pandas_errors(self, mock_read_excel, sample_excel_file):
        """Test handling of pandas read errors."""
        mock_read_excel.side_effect = pd.errors.EmptyDataError("No data")
        
        with pytest.raises(pd.errors.EmptyDataError):
            list(self.excel_processor.read_excel_file_stream(str(sample_excel_file), start_row=2))
    
    def test_validate_excel_structure_case_sensitivity(self, temp_dir):
        """Test column validation with case differences."""
        # Create Excel file with different case
        file_path = temp_dir / "case_test.xlsx"
        df = pd.DataFrame({
            "purchase date": ["2025-01-20"],  # lowercase
            "Customer Email": ["test@email.com"],
            "PRODUCT NAME": ["Test"]  # uppercase
        })
        df.to_excel(file_path, index=False)
        
        expected_columns = ["Purchase Date", "Customer Email", "Product Name"]
        
        result = self.excel_processor.validate_excel_structure(
            str(file_path),
            expected_columns,
            header_row=1
        )
        
        # Should handle case differences appropriately
        assert isinstance(result, ValidationResult)
    
    def test_preview_excel_data_empty_file(self, temp_dir):
        """Test preview of empty Excel file."""
        file_path = temp_dir / "empty.xlsx"
        df = pd.DataFrame()  # Empty dataframe
        df.to_excel(file_path, index=False)
        
        result = self.excel_processor.preview_excel_data(str(file_path), start_row=2, limit=5)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_get_excel_column_names_with_nan_columns(self, temp_dir):
        """Test column extraction when some columns have NaN names."""
        file_path = temp_dir / "nan_columns.xlsx"
        # Create DataFrame with some empty column names
        df = pd.DataFrame({
            "Valid Column": [1, 2, 3],
            "": [4, 5, 6],  # Empty column name
            "Another Valid": [7, 8, 9]
        })
        df.to_excel(file_path, index=False)
        
        result = self.excel_processor.get_excel_column_names(str(file_path), header_row=1)
        
        # Should handle NaN/empty column names gracefully
        assert isinstance(result, list)
        assert "Valid Column" in result
        assert "Another Valid" in result



