"""
Excel Processing Module

Handles Excel file reading, validation, column extraction, and data type detection.
Supports large file handling with streaming capabilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Iterator
from dataclasses import dataclass
from datetime import datetime
import hashlib
import logging

from config.settings import get_settings

logger = logging.getLogger(__name__)

@dataclass
class ExcelFileInfo:
    """Information about an Excel file."""
    file_path: Path
    file_name: str
    file_size: int
    file_hash: str
    sheet_names: List[str]
    total_rows: int
    total_columns: int
    column_names: List[str]
    data_start_row: int
    created_at: datetime

@dataclass
class ColumnInfo:
    """Information about a column in Excel file."""
    name: str
    index: int
    data_type: str
    sample_values: List[Any]
    null_count: int
    unique_count: int
    is_required: bool

class ExcelProcessor:
    """Processes Excel files for data ingestion."""
    
    def __init__(self):
        """Initialize Excel processor."""
        self.settings = get_settings()
        self.chunk_size = 1000  # Process in chunks for large files
        
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate Excel file before processing.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        logger.info(f"🔍 Validating Excel file: {file_path}")
        
        try:
            # Check if file exists
            if not file_path.exists():
                logger.error(f"❌ File does not exist: {file_path}")
                return False
            
            # Check file size (max 100MB)
            file_size = file_path.stat().st_size
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                logger.error(f"❌ File too large: {file_size / 1024 / 1024:.1f}MB > 100MB")
                return False
            
            # Check file extension
            if file_path.suffix.lower() not in ['.xlsx', '.xls', '.xlsm']:
                logger.error(f"❌ Invalid file extension: {file_path.suffix}")
                return False
            
            # Try to read file structure
            try:
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                logger.info(f"✅ File valid with {len(sheet_names)} sheets: {sheet_names}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Cannot read Excel file: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ File validation failed: {e}")
            return False
    
    def get_file_info(self, file_path: Path, sheet_name: Optional[str] = None) -> ExcelFileInfo:
        """
        Get comprehensive information about Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name (uses first sheet if None)
            
        Returns:
            ExcelFileInfo: Complete file information
        """
        logger.info(f"📊 Analyzing Excel file: {file_path}")
        
        try:
            # Basic file info
            file_size = file_path.stat().st_size
            file_hash = self._calculate_file_hash(file_path)
            
            # Read Excel structure
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            # Use first sheet if not specified
            target_sheet = sheet_name or sheet_names[0]
            logger.info(f"📋 Using sheet: {target_sheet}")
            
            # Read first few rows to analyze structure
            df_sample = pd.read_excel(file_path, sheet_name=target_sheet, nrows=10)
            column_names = df_sample.columns.tolist()
            
            # Get total row count (more efficient)
            df_full = pd.read_excel(file_path, sheet_name=target_sheet)
            total_rows = len(df_full)
            total_columns = len(df_full.columns)
            
            # Detect data start row (skip headers and empty rows)
            data_start_row = self._detect_data_start_row(df_full)
            
            logger.info(f"✅ File analysis complete: {total_rows} rows, {total_columns} columns")
            
            return ExcelFileInfo(
                file_path=file_path,
                file_name=file_path.name,
                file_size=file_size,
                file_hash=file_hash,
                sheet_names=sheet_names,
                total_rows=total_rows,
                total_columns=total_columns,
                column_names=column_names,
                data_start_row=data_start_row,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze Excel file: {e}")
            raise
    
    def extract_columns(self, file_path: Path, sheet_name: Optional[str] = None) -> List[ColumnInfo]:
        """
        Extract detailed column information from Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name (uses first sheet if None)
            
        Returns:
            List[ColumnInfo]: Detailed column information
        """
        logger.info(f"🔍 Extracting column information from: {file_path}")
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            columns_info = []
            
            for idx, column_name in enumerate(df.columns):
                column_data = df[column_name]
                
                # Detect data type
                data_type = self._detect_column_type(column_data)
                
                # Get sample values (non-null)
                sample_values = column_data.dropna().head(5).tolist()
                
                # Calculate statistics
                null_count = column_data.isnull().sum()
                unique_count = column_data.nunique()
                is_required = null_count == 0
                
                column_info = ColumnInfo(
                    name=str(column_name),
                    index=idx,
                    data_type=data_type,
                    sample_values=sample_values,
                    null_count=int(null_count),
                    unique_count=int(unique_count),
                    is_required=is_required
                )
                
                columns_info.append(column_info)
                logger.debug(f"📋 Column: {column_name} -> {data_type} ({unique_count} unique, {null_count} nulls)")
            
            logger.info(f"✅ Extracted {len(columns_info)} columns")
            return columns_info
            
        except Exception as e:
            logger.error(f"❌ Failed to extract columns: {e}")
            raise
    
    def read_data_chunked(self, file_path: Path, sheet_name: Optional[str] = None, 
                         start_row: int = 1, chunk_size: Optional[int] = None) -> Iterator[pd.DataFrame]:
        """
        Read Excel data in chunks for memory-efficient processing.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name
            start_row: Row to start reading data (1-based)
            chunk_size: Number of rows per chunk
            
        Yields:
            pd.DataFrame: Data chunk
        """
        chunk_size = chunk_size or self.chunk_size
        logger.info(f"📖 Reading Excel data in chunks of {chunk_size} rows, starting from row {start_row}")
        
        try:
            # Try to read the file with different approaches to handle various Excel structures
            df_full = None
            
            # Approach 1: Try reading with default settings
            try:
                # Don't specify sheet_name, use the first sheet
                df_full = pd.read_excel(file_path, engine='openpyxl')
                # Handle case where read_excel returns a dict
                if isinstance(df_full, dict):
                    df_full = pd.DataFrame([df_full])
                logger.debug(f"✅ Successfully read with default settings: shape={df_full.shape}")
            except Exception as e:
                logger.debug(f"⚠️ Default reading failed: {e}")
            
            # Approach 2: If that failed or produced wrong structure, try with header=None
            if df_full is None or (hasattr(df_full, 'shape') and df_full.shape[1] == 1):
                try:
                    logger.debug("🔄 Trying with header=None...")
                    # Don't specify sheet_name, use the first sheet
                    df_full = pd.read_excel(file_path, header=None, engine='openpyxl')
                    # Handle case where read_excel returns a dict
                    if isinstance(df_full, dict):
                        df_full = pd.DataFrame([df_full])
                    logger.debug(f"✅ Successfully read with header=None: shape={df_full.shape}")
                    
                    # If we have more than 1 row, use the first row as headers
                    if len(df_full) > 1:
                        headers = df_full.iloc[0].tolist()
                        df_full = df_full.iloc[1:].copy()
                        df_full.columns = headers
                        logger.debug(f"✅ Set headers from first row: {headers}")
                except Exception as e:
                    logger.debug(f"⚠️ Header=None reading failed: {e}")
            
            # Handle case where read_excel returns a dict (final check)
            if isinstance(df_full, dict):
                df_full = pd.DataFrame([df_full])
            
            if df_full is None:
                raise ValueError("Failed to read Excel file with any method")
            
            total_rows = len(df_full)
            column_names = df_full.columns.tolist()
            
            logger.info(f"📊 Total rows to process: {total_rows}")
            logger.debug(f"📋 Column names: {column_names}")
            
            # If start_row > 1, we need to skip the header rows
            if start_row > 1:
                # Skip the first (start_row-1) rows
                df_full = df_full.iloc[start_row-1:].copy()
                total_rows = len(df_full)
                logger.debug(f"📊 After skipping rows: {total_rows} rows remaining")
            
            # Read in chunks by slicing the full DataFrame
            current_row = 0  # Start from beginning of loaded data
            chunk_count = 0
            
            logger.debug(f"🔍 Starting chunking: total_rows={total_rows}, chunk_size={chunk_size}")
            
            while current_row < total_rows:
                # Calculate chunk size for this iteration
                remaining_rows = total_rows - current_row
                actual_chunk_size = min(chunk_size, remaining_rows)
                
                logger.debug(f"🔍 Chunk iteration: current_row={current_row}, remaining_rows={remaining_rows}, actual_chunk_size={actual_chunk_size}")
                
                if actual_chunk_size <= 0:
                    logger.debug(f"🔍 Breaking: actual_chunk_size={actual_chunk_size}")
                    break
                
                # Slice the DataFrame to get the chunk
                chunk = df_full.iloc[current_row:current_row + actual_chunk_size].copy()
                
                # Reset index for the chunk
                chunk.reset_index(drop=True, inplace=True)
                
                chunk_count += 1
                logger.debug(f"📦 Processing chunk {chunk_count}: rows {current_row + 1}-{current_row + len(chunk)}")
                logger.debug(f"📦 Chunk shape: {chunk.shape}, columns: {list(chunk.columns)}")
                
                yield chunk
                
                current_row += actual_chunk_size
                logger.debug(f"🔍 Updated current_row to: {current_row}")
            
            logger.info(f"✅ Completed reading {chunk_count} chunks")
            
        except Exception as e:
            logger.error(f"❌ Failed to read Excel data: {e}")
            raise
    
    def preview_data(self, file_path: Path, sheet_name: Optional[str] = None, 
                    start_row: int = 1, num_rows: int = 5) -> pd.DataFrame:
        """
        Preview Excel data for user verification.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name
            start_row: Row to start preview (1-based)
            num_rows: Number of rows to preview
            
        Returns:
            pd.DataFrame: Preview data
        """
        logger.info(f"👀 Previewing {num_rows} rows starting from row {start_row}")
        
        try:
            # Read preview data
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=start_row - 1,
                nrows=num_rows,
                header=0
            )
            
            logger.info(f"✅ Preview loaded: {len(df)} rows x {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to preview data: {e}")
            raise
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for duplicate detection."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _detect_data_start_row(self, df: pd.DataFrame) -> int:
        """
        Detect the row where actual data starts (skip headers and empty rows).
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            int: Data start row (1-based)
        """
        # Simple heuristic: find first row with mostly non-null values
        for idx, row in df.iterrows():
            non_null_ratio = row.notna().sum() / len(row)
            if non_null_ratio > 0.5:  # At least 50% non-null values
                return idx + 2  # Convert to 1-based and account for header
        
        return 2  # Default to row 2 (after header)
    
    def _detect_column_type(self, column_data: pd.Series) -> str:
        """
        Detect the most appropriate data type for a column.
        
        Args:
            column_data: Column data to analyze
            
        Returns:
            str: Detected data type
        """
        # Remove null values for type detection
        clean_data = column_data.dropna()
        
        if clean_data.empty:
            return "string"
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(clean_data):
            return "datetime"
        
        # Try to convert to datetime
        try:
            pd.to_datetime(clean_data.head(10), errors='raise')
            return "datetime"
        except:
            pass
        
        # Check for numeric types
        if pd.api.types.is_numeric_dtype(clean_data):
            if pd.api.types.is_integer_dtype(clean_data):
                return "integer"
            else:
                return "decimal"
        
        # Try to convert to numeric
        try:
            pd.to_numeric(clean_data.head(10), errors='raise')
            return "decimal"
        except:
            pass
        
        # Check for boolean
        if pd.api.types.is_bool_dtype(clean_data):
            return "boolean"
        
        # Check if it looks like boolean values
        unique_values = set(str(v).lower() for v in clean_data.unique()[:10])
        boolean_values = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
        if unique_values.issubset(boolean_values):
            return "boolean"
        
        # Default to string
        return "string"