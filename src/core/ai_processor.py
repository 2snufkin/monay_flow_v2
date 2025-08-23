"""
AI Integration Module

Handles OpenAI API integration for schema processing and normalization.
"""

import json
import time
from typing import List, Dict, Any
import openai

from models.schema_definition import AISchemaResponse, AttributeDefinition, IndexDefinition
from config.settings import get_settings


class AISchemaProcessor:
    """Processes column names using OpenAI API to generate normalized schemas."""
    
    def __init__(self):
        """Initialize AISchemaProcessor."""
        self._settings = None
    
    @property
    def settings(self):
        """Lazy load settings when needed."""
        if self._settings is None:
            self._settings = get_settings()
        return self._settings
    
    def process_columns(self, column_names: List[str]) -> AISchemaResponse:
        """
        Send column names to OpenAI API and parse the response.
        
        Args:
            column_names: Raw column names from Excel header
            
        Returns:
            Structured AI response with normalized attributes and suggestions
            
        Raises:
            AIProcessingError: If API call fails or response is invalid
        """
        if not column_names:
            raise ValueError("Column names list cannot be empty")
        
        try:
            # Create the API request using OpenAI v1.0+ syntax
            from openai import OpenAI
            client = OpenAI(api_key=self.settings.ai.openai_api_key)
            
            response = client.chat.completions.create(
                model=self.settings.ai.openai_model,
                messages=[
                    {"role": "system", "content": self.generate_system_prompt()},
                    {"role": "user", "content": self.generate_user_prompt(column_names)}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=1000
            )
            
            # Parse the response (OpenAI v1.0+ syntax)
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response content from OpenAI API")
            ai_response = json.loads(content)
            
            # Validate the response
            if not self.validate_ai_response(ai_response):
                raise ValueError("Invalid AI response structure")
            
            # Convert to our data models
            normalized_attributes = {}
            for excel_col, attr_data in ai_response["normalized_attributes"].items():
                normalized_attributes[excel_col] = AttributeDefinition(
                    field_name=attr_data["field_name"],
                    data_type=attr_data["data_type"],
                    description=attr_data["description"],
                    is_required=attr_data.get("is_required", False)
                )
            
            suggested_indexes = []
            for idx_data in ai_response["suggested_indexes"]:
                suggested_indexes.append(IndexDefinition(
                    field_names=idx_data["field_names"] if isinstance(idx_data["field_names"], list) else [idx_data["field_names"]],
                    index_type=idx_data["index_type"],
                    reason=idx_data["reason"]
                ))
            
            return AISchemaResponse(
                normalized_attributes=normalized_attributes,
                suggested_indexes=suggested_indexes,
                duplicate_detection_columns=ai_response["duplicate_detection_columns"],
                collection_name=ai_response["collection_name"]
            )
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to parse AI response as JSON: {e}", e.doc, e.pos)
        except Exception as e:
            raise Exception(f"AI processing failed: {str(e)}")
    
    def validate_ai_response(self, response: dict) -> bool:
        """
        Validate AI response structure and content integrity.
        
        Args:
            response: Raw response from OpenAI API
            
        Returns:
            True if response is valid and usable
        """
        if not isinstance(response, dict):
            return False
        
        required_keys = ["normalized_attributes", "suggested_indexes", "duplicate_detection_columns", "collection_name"]
        
        # Check all required keys exist
        for key in required_keys:
            if key not in response:
                return False
        
        # Validate normalized_attributes structure
        if not isinstance(response["normalized_attributes"], dict):
            return False
        
        # Validate suggested_indexes structure
        if not isinstance(response["suggested_indexes"], list):
            return False
        
        # Validate duplicate_detection_columns structure
        if not isinstance(response["duplicate_detection_columns"], list):
            return False
        
        # Validate collection_name
        if not isinstance(response["collection_name"], str) or not response["collection_name"].strip():
            return False
        
        return True
    
    def generate_system_prompt(self) -> str:
        """
        Generate the system prompt for OpenAI API calls.
        
        Returns:
            Formatted system prompt string
        """
        return """You are a database schema expert. Given a list of Excel column names, you will:

1. Normalize column names to proper database field names (snake_case, descriptive)
2. Infer appropriate data types based on column names
3. Suggest database indexes for optimal performance
4. Recommend columns for duplicate detection logic

Return your response as a JSON object with the following structure:
{
  "normalized_attributes": {
    "Original Column Name": {
      "field_name": "normalized_field_name",
      "data_type": "String|Number|Date|Boolean",
      "description": "Brief description of the field"
    }
  },
  "suggested_indexes": [
    {
      "field_names": ["field1", "field2"],
      "index_type": "unique|ascending|descending|text",
      "reason": "Why this index is recommended"
    }
  ],
  "duplicate_detection_columns": ["field1", "field2", "field3"],
  "collection_name": "suggested_mongodb_collection_name"
}

Be conservative with duplicate detection - only suggest fields that are truly unique identifiers."""
    
    def generate_user_prompt(self, columns: List[str]) -> str:
        """
        Generate user prompt with column data for AI processing.
        
        Args:
            columns: List of column names to process
            
        Returns:
            Formatted user prompt string
        """
        columns_text = "\n".join([f"- {col}" for col in columns])
        
        return f"""Analyze these Excel column names and create a database schema:

Column Names:
{columns_text}

Context: This is for a data ingestion system where users will upload Excel files with this structure repeatedly. Focus on practical database design and duplicate prevention."""
    
    def retry_ai_request(self, columns: List[str], max_retries: int = 3) -> AISchemaResponse:
        """
        Retry AI processing with exponential backoff on failure.
        
        Args:
            columns: Column names to process
            max_retries: Maximum number of retry attempts
            
        Returns:
            AI response or raises exception after max retries
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return self.process_columns(columns)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
        
        # If we get here, all retries failed
        if isinstance(last_exception, Exception):
            raise last_exception
        else:
            raise RuntimeError(f"AI processing failed after {max_retries} attempts: {last_exception}")
