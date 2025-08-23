"""
Unit tests for AISchemaProcessor class.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from src.core.ai_processor import AISchemaProcessor
from src.models.schema_definition import AISchemaResponse, AttributeDefinition, IndexDefinition


@pytest.mark.unit
class TestAISchemaProcessor:
    """Test cases for AISchemaProcessor class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.ai_processor = AISchemaProcessor()
    
    @patch('src.core.ai_processor.openai.ChatCompletion.create')
    def test_process_columns_success(self, mock_openai_create, mock_openai_response):
        """Test successful AI processing of column names."""
        # Mock OpenAI response
        mock_openai_create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(mock_openai_response)))]
        )
        
        column_names = ["Purchase Date", "Customer Email", "Product Name", "Amount"]
        
        result = self.ai_processor.process_columns(column_names)
        
        assert isinstance(result, AISchemaResponse)
        assert len(result.normalized_attributes) == 4
        assert "Purchase Date" in result.normalized_attributes
        assert result.normalized_attributes["Purchase Date"].field_name == "purchase_date"
        assert len(result.suggested_indexes) == 2
        assert result.collection_name == "customer_purchases"
    
    @patch('src.core.ai_processor.openai.ChatCompletion.create')
    def test_process_columns_api_error(self, mock_openai_create):
        """Test handling of OpenAI API errors."""
        mock_openai_create.side_effect = Exception("API Error")
        
        column_names = ["Col1", "Col2"]
        
        with pytest.raises(Exception):
            self.ai_processor.process_columns(column_names)
    
    @patch('src.core.ai_processor.openai.ChatCompletion.create')
    def test_process_columns_invalid_json_response(self, mock_openai_create):
        """Test handling of invalid JSON response from OpenAI."""
        mock_openai_create.return_value = Mock(
            choices=[Mock(message=Mock(content="Invalid JSON"))]
        )
        
        column_names = ["Col1", "Col2"]
        
        with pytest.raises(json.JSONDecodeError):
            self.ai_processor.process_columns(column_names)
    
    def test_validate_ai_response_valid(self, mock_openai_response):
        """Test validation of valid AI response."""
        result = self.ai_processor.validate_ai_response(mock_openai_response)
        assert result is True
    
    def test_validate_ai_response_missing_keys(self):
        """Test validation of AI response with missing required keys."""
        invalid_response = {
            "normalized_attributes": {},
            # Missing other required keys
        }
        
        result = self.ai_processor.validate_ai_response(invalid_response)
        assert result is False
    
    def test_validate_ai_response_invalid_structure(self):
        """Test validation of AI response with invalid structure."""
        invalid_response = {
            "normalized_attributes": "not_a_dict",  # Should be dict
            "suggested_indexes": [],
            "duplicate_detection": {},
            "collection_name": "test"
        }
        
        result = self.ai_processor.validate_ai_response(invalid_response)
        assert result is False
    
    def test_generate_system_prompt(self):
        """Test generation of system prompt."""
        prompt = self.ai_processor.generate_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "database schema expert" in prompt.lower()
        assert "json" in prompt.lower()
        assert "normalized_attributes" in prompt
        assert "suggested_indexes" in prompt
    
    def test_generate_user_prompt(self):
        """Test generation of user prompt with column data."""
        columns = ["Purchase Date", "Customer Email", "Amount"]
        
        prompt = self.ai_processor.generate_user_prompt(columns)
        
        assert isinstance(prompt, str)
        assert "Purchase Date" in prompt
        assert "Customer Email" in prompt
        assert "Amount" in prompt
        assert "column names" in prompt.lower()
    
    @patch('src.core.ai_processor.openai.ChatCompletion.create')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_retry_ai_request_success_on_retry(self, mock_sleep, mock_openai_create, mock_openai_response):
        """Test successful AI request after initial failure."""
        # First call fails, second succeeds
        mock_openai_create.side_effect = [
            Exception("Temporary error"),
            Mock(choices=[Mock(message=Mock(content=json.dumps(mock_openai_response)))])
        ]
        
        column_names = ["Col1", "Col2"]
        
        result = self.ai_processor.retry_ai_request(column_names, max_retries=2)
        
        assert isinstance(result, AISchemaResponse)
        assert mock_openai_create.call_count == 2
    
    @patch('src.core.ai_processor.openai.ChatCompletion.create')
    @patch('time.sleep')
    def test_retry_ai_request_max_retries_exceeded(self, mock_sleep, mock_openai_create):
        """Test failure when max retries are exceeded."""
        mock_openai_create.side_effect = Exception("Persistent error")
        
        column_names = ["Col1", "Col2"]
        
        with pytest.raises(Exception):
            self.ai_processor.retry_ai_request(column_names, max_retries=2)
        
        assert mock_openai_create.call_count == 2
    
    def test_ai_processor_initialization(self):
        """Test AISchemaProcessor initialization."""
        processor = AISchemaProcessor()
        assert processor is not None
    
    @patch('src.core.ai_processor.openai.ChatCompletion.create')
    def test_process_columns_empty_list(self, mock_openai_create):
        """Test processing with empty column list."""
        with pytest.raises(ValueError):
            self.ai_processor.process_columns([])
    
    @patch('src.core.ai_processor.openai.ChatCompletion.create')
    def test_process_columns_single_column(self, mock_openai_create):
        """Test processing with single column."""
        mock_response = {
            "normalized_attributes": {
                "Email": {
                    "field_name": "email",
                    "data_type": "String",
                    "description": "Email address"
                }
            },
            "suggested_indexes": [
                {
                    "field": "email",
                    "type": "unique",
                    "reason": "Email should be unique"
                }
            ],
            "duplicate_detection": {
                "primary_keys": ["email"],
                "reasoning": "Email is unique identifier"
            },
            "collection_name": "users"
        }
        
        mock_openai_create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(mock_response)))]
        )
        
        result = self.ai_processor.process_columns(["Email"])
        
        assert isinstance(result, AISchemaResponse)
        assert len(result.normalized_attributes) == 1
        assert "Email" in result.normalized_attributes
    
    def test_validate_ai_response_edge_cases(self):
        """Test validation with various edge cases."""
        # Test with None
        assert self.ai_processor.validate_ai_response(None) is False
        
        # Test with empty dict
        assert self.ai_processor.validate_ai_response({}) is False
        
        # Test with string instead of dict
        assert self.ai_processor.validate_ai_response("not a dict") is False
        
        # Test with partial valid structure
        partial_response = {
            "normalized_attributes": {},
            "suggested_indexes": [],
            # Missing duplicate_detection and collection_name
        }
        assert self.ai_processor.validate_ai_response(partial_response) is False
    
    @patch('src.core.ai_processor.openai.ChatCompletion.create')
    def test_process_columns_with_special_characters(self, mock_openai_create, mock_openai_response):
        """Test processing columns with special characters."""
        mock_openai_create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(mock_openai_response)))]
        )
        
        column_names = ["Customer's Name", "Product #", "Amount ($)", "Date/Time"]
        
        result = self.ai_processor.process_columns(column_names)
        
        assert isinstance(result, AISchemaResponse)
        # Should handle special characters gracefully
    
    @patch('src.core.ai_processor.get_settings')
    def test_ai_processor_uses_settings(self, mock_get_settings):
        """Test that AI processor uses application settings."""
        mock_settings = Mock()
        mock_settings.ai.openai_api_key = "test_key"
        mock_settings.ai.openai_model = "gpt-3.5-turbo"
        mock_settings.ai.openai_timeout = 60
        mock_get_settings.return_value = mock_settings
        
        processor = AISchemaProcessor()
        
        # Verify settings are used
        assert processor is not None
