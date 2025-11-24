"""
Unit tests for openrouter_client module.

Demonstrates testability of helper functions and client functionality.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from openrouter_client import (
    OpenRouterClient,
    OpenRouterResponse,
    OpenRouterError,
    OpenRouterConnectionError,
    OpenRouterAuthenticationError,
    OpenRouterRateLimitError,
    OpenRouterAPIError,
    OpenRouterParsingError,
    extract_json_from_text,
    extract_content_from_response,
    simple_chat,
    batch_chat,
)


class TestHelperFunctions:
    """Tests for standalone helper functions."""
    
    def test_extract_json_from_text_valid(self):
        """Test extracting valid JSON from text."""
        text = 'Here is some text {"key": "value", "number": 42} and more text'
        result = extract_json_from_text(text)
        assert result == {"key": "value", "number": 42}
    
    def test_extract_json_from_text_with_trailing_comma(self):
        """Test extracting JSON with trailing comma (common LLM error)."""
        text = '{"key": "value", "number": 42,}'
        result = extract_json_from_text(text)
        assert result == {"key": "value", "number": 42}
    
    def test_extract_json_from_text_no_json(self):
        """Test error when no JSON present."""
        text = "This is just plain text without any JSON"
        with pytest.raises(OpenRouterParsingError):
            extract_json_from_text(text)
    
    def test_extract_json_from_text_invalid_json(self):
        """Test error on invalid JSON."""
        text = '{"key": "value", invalid}'
        with pytest.raises(OpenRouterParsingError):
            extract_json_from_text(text)
    
    def test_extract_content_from_response_openai_format(self):
        """Test extracting content from standard OpenAI format."""
        data = {
            "choices": [
                {
                    "message": {
                        "content": "Hello, world!"
                    }
                }
            ]
        }
        result = extract_content_from_response(data)
        assert result == "Hello, world!"
    
    def test_extract_content_from_response_alternative_format(self):
        """Test extracting content from alternative formats."""
        data = {"output": "Alternative format"}
        result = extract_content_from_response(data)
        assert result == "Alternative format"
    
    def test_extract_content_from_response_string(self):
        """Test extracting content when response is already a string."""
        result = extract_content_from_response("Direct string")
        assert result == "Direct string"
    
    def test_extract_content_from_response_no_content(self):
        """Test error when no content found."""
        data = {"some": "data", "but": "no content"}
        with pytest.raises(OpenRouterParsingError):
            extract_content_from_response(data)


class TestOpenRouterResponse:
    """Tests for OpenRouterResponse dataclass."""
    
    def test_response_creation_success(self):
        """Test creating a successful response."""
        response = OpenRouterResponse(
            content="Test content",
            model="gpt-4",
            success=True,
            latency_ms=123.45
        )
        assert response.content == "Test content"
        assert response.model == "gpt-4"
        assert response.success is True
        assert response.latency_ms == 123.45
        assert response.error is None
    
    def test_response_creation_failure(self):
        """Test creating a failure response."""
        response = OpenRouterResponse(
            content="",
            model="gpt-4",
            success=False,
            latency_ms=100.0,
            error="API error occurred"
        )
        assert response.success is False
        assert response.error == "API error occurred"
    
    def test_response_post_init_validation(self):
        """Test post-initialization validation."""
        response = OpenRouterResponse(
            content="",
            model="gpt-4",
            success=True,
            latency_ms=100.0
        )
        assert response.success is False
        assert response.error == "Empty content received"
    
    def test_response_to_dict(self):
        """Test converting response to dictionary."""
        response = OpenRouterResponse(
            content="Test",
            model="gpt-4",
            success=True,
            latency_ms=100.0
        )
        result = response.to_dict()
        assert isinstance(result, dict)
        assert result["content"] == "Test"
        assert result["model"] == "gpt-4"
        assert result["success"] is True
        assert "timestamp" in result


class TestOpenRouterClient:
    """Tests for OpenRouterClient class."""
    
    def test_client_initialization(self):
        """Test client initialization with parameters."""
        client = OpenRouterClient(
            api_key="test-key",
            model="gpt-4",
            timeout=60.0,
            max_retries=3
        )
        assert client.api_key == "test-key"
        assert client.model == "gpt-4"
        assert client.timeout == 60.0
        assert client.max_retries == 3
    
    def test_client_default_values(self):
        """Test client uses default values."""
        client = OpenRouterClient(api_key="test-key")
        assert client.model == "gpt-4o-mini"
        assert client.timeout == 30.0
        assert client.max_retries == 2
        assert client.api_url == "https://openrouter.ai/api/v1/chat/completions"
    
    def test_build_payload_basic(self):
        """Test building basic request payload."""
        client = OpenRouterClient(api_key="test-key", model="gpt-4")
        messages = [{"role": "user", "content": "Hello"}]
        payload = client._build_payload(messages)
        
        assert payload["model"] == "gpt-4"
        assert payload["messages"] == messages
        assert "max_tokens" not in payload
        assert "temperature" not in payload
    
    def test_build_payload_with_params(self):
        """Test building payload with optional parameters."""
        client = OpenRouterClient(api_key="test-key", model="gpt-4")
        messages = [{"role": "user", "content": "Hello"}]
        payload = client._build_payload(
            messages,
            max_tokens=100,
            temperature=0.7,
            custom_param="test"
        )
        
        assert payload["max_tokens"] == 100
        assert payload["temperature"] == 0.7
        assert payload["custom_param"] == "test"
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client works as async context manager."""
        async with OpenRouterClient(api_key="test-key") as client:
            assert client._client is not None
        
        assert client._client is None
    
    @pytest.mark.asyncio
    async def test_client_requires_initialization(self):
        """Test client raises error if not initialized."""
        client = OpenRouterClient(api_key="test-key")
        
        with pytest.raises(RuntimeError, match="Client not initialized"):
            client._validate_client()
    
    @pytest.mark.asyncio
    async def test_chat_builds_correct_messages(self):
        """Test chat method builds correct message structure."""
        mock_response = OpenRouterResponse(
            content="Hello!",
            model="gpt-4",
            success=True,
            latency_ms=100.0
        )
        
        async with OpenRouterClient(api_key="test-key") as client:
            with patch.object(client, '_make_request', return_value=mock_response) as mock:
                await client.chat(
                    prompt="Hi",
                    system_prompt="You are helpful",
                    max_tokens=50,
                    temperature=0.5
                )
                
                call_args = mock.call_args
                payload = call_args[0][0]
                
                assert len(payload["messages"]) == 2
                assert payload["messages"][0]["role"] == "system"
                assert payload["messages"][0]["content"] == "You are helpful"
                assert payload["messages"][1]["role"] == "user"
                assert payload["messages"][1]["content"] == "Hi"
                assert payload["max_tokens"] == 50
                assert payload["temperature"] == 0.5
    
    @pytest.mark.asyncio
    async def test_chat_without_system_prompt(self):
        """Test chat method without system prompt."""
        mock_response = OpenRouterResponse(
            content="Hello!",
            model="gpt-4",
            success=True,
            latency_ms=100.0
        )
        
        async with OpenRouterClient(api_key="test-key") as client:
            with patch.object(client, '_make_request', return_value=mock_response) as mock:
                await client.chat(prompt="Hi")
                
                call_args = mock.call_args
                payload = call_args[0][0]
                
                assert len(payload["messages"]) == 1
                assert payload["messages"][0]["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_chat_with_json_parsing(self):
        """Test chat method with JSON parsing enabled."""
        mock_response = OpenRouterResponse(
            content='{"result": "success"}',
            model="gpt-4",
            success=True,
            latency_ms=100.0
        )
        
        async with OpenRouterClient(api_key="test-key") as client:
            with patch.object(client, '_make_request', return_value=mock_response):
                response = await client.chat(prompt="Hi", parse_json=True)
                
                assert response.parsed_json == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_chat_many_concurrent(self):
        """Test sending multiple prompts concurrently."""
        async with OpenRouterClient(api_key="test-key") as client:
            prompts = ["Hi", "Hello", "Hey"]
            
            mock_responses = [
                OpenRouterResponse(
                    content=f"Response {i}",
                    model="gpt-4",
                    success=True,
                    latency_ms=100.0
                )
                for i in range(len(prompts))
            ]
            
            with patch.object(client, 'chat', side_effect=mock_responses):
                responses = await client.chat_many(prompts)
                
                assert len(responses) == 3
                assert all(isinstance(r, OpenRouterResponse) for r in responses)
    
    @pytest.mark.asyncio
    async def test_custom_request(self):
        """Test custom request with full message control."""
        mock_response = OpenRouterResponse(
            content="Custom response",
            model="gpt-4",
            success=True,
            latency_ms=100.0
        )
        
        messages = [
            {"role": "system", "content": "You are a bot"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"}
        ]
        
        async with OpenRouterClient(api_key="test-key") as client:
            with patch.object(client, '_make_request', return_value=mock_response):
                response = await client.custom_request(messages)
                
                assert response.content == "Custom response"


class TestConvenienceFunctions:
    """Tests for convenience wrapper functions."""
    
    @pytest.mark.asyncio
    async def test_simple_chat(self):
        """Test simple_chat convenience function."""
        mock_response = OpenRouterResponse(
            content="Test response",
            model="gpt-4",
            success=True,
            latency_ms=100.0
        )
        
        with patch('openrouter_client.OpenRouterClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            response = await simple_chat(
                api_key="test-key",
                prompt="Hello",
                model="gpt-4"
            )
            
            assert response.content == "Test response"
    
    @pytest.mark.asyncio
    async def test_batch_chat(self):
        """Test batch_chat convenience function."""
        mock_responses = [
            OpenRouterResponse(
                content=f"Response {i}",
                model="gpt-4",
                success=True,
                latency_ms=100.0
            )
            for i in range(3)
        ]
        
        with patch('openrouter_client.OpenRouterClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.chat_many = AsyncMock(return_value=mock_responses)
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            responses = await batch_chat(
                api_key="test-key",
                prompts=["Hi", "Hello", "Hey"]
            )
            
            assert len(responses) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
