"""
OpenRouter API Client

An async httpx-based client for sending prompts to OpenRouter with:
- Session-level AsyncClient reuse
- Configurable headers (API key, model)
- Structured request payloads
- Exponential backoff retries
- Timeout handling
- JSON-formatted response parsing
- Concurrent request support (asyncio.gather)
- Standardized result objects with metadata
- Graceful fallbacks for API failures
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import httpx


# ---------------------------
# Custom Exceptions
# ---------------------------

class OpenRouterError(Exception):
    """Base exception for OpenRouter client errors."""
    pass


class OpenRouterConnectionError(OpenRouterError):
    """Raised when connection to OpenRouter API fails."""
    pass


class OpenRouterAuthenticationError(OpenRouterError):
    """Raised when API key authentication fails."""
    pass


class OpenRouterRateLimitError(OpenRouterError):
    """Raised when rate limit is exceeded."""
    pass


class OpenRouterAPIError(OpenRouterError):
    """Raised for general API errors."""
    pass


class OpenRouterParsingError(OpenRouterError):
    """Raised when response parsing fails."""
    pass


# ---------------------------
# Result Models
# ---------------------------

@dataclass
class OpenRouterResponse:
    """Standardized response object from OpenRouter API."""
    
    content: str
    model: str
    success: bool
    latency_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    parsed_json: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate and clean up response data."""
        if self.success and not self.content:
            self.success = False
            self.error = "Empty content received"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        return {
            "content": self.content,
            "model": self.model,
            "success": self.success,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "parsed_json": self.parsed_json,
        }


# ---------------------------
# Helper Functions
# ---------------------------

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Attempts to find and parse the first JSON object in text.
    
    Args:
        text: Text potentially containing a JSON object
        
    Returns:
        Parsed JSON object as dictionary
        
    Raises:
        OpenRouterParsingError: If no valid JSON found
    """
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1 or end <= start:
        raise OpenRouterParsingError("No JSON object found in text")
    
    candidate = text[start:end+1]
    
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        # Attempt to clean up common LLM JSON errors (trailing commas, etc.)
        cleaned = re.sub(r',\s*([\]}])', r'\1', candidate)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e2:
            raise OpenRouterParsingError(
                f"Failed to parse JSON from text: {e2}"
            ) from e2


def extract_content_from_response(data: Union[Dict[str, Any], str]) -> str:
    """
    Extract text content from various OpenRouter response formats.
    
    Args:
        data: Response data from OpenRouter API
        
    Returns:
        Extracted text content
        
    Raises:
        OpenRouterParsingError: If content cannot be extracted
    """
    if isinstance(data, str):
        return data
    
    if not isinstance(data, dict):
        raise OpenRouterParsingError(f"Unexpected response type: {type(data)}")
    
    # Try standard OpenAI format
    choices = data.get("choices")
    if choices and isinstance(choices, list) and len(choices) > 0:
        choice = choices[0]
        if isinstance(choice, dict):
            message = choice.get("message") or choice
            if isinstance(message, dict):
                content = message.get("content")
                if content:
                    return content
    
    # Try alternative formats
    for key in ["output", "text", "content"]:
        content = data.get(key)
        if content and isinstance(content, str):
            return content
    
    raise OpenRouterParsingError("No textual content found in response")


async def exponential_backoff_retry(
    coro_func,
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    backoff_multiplier: float = 2.0,
    max_backoff: float = 60.0,
    retryable_exceptions: tuple = (httpx.TimeoutException, httpx.ConnectError)
):
    """
    Execute an async function with exponential backoff retry logic.
    
    Args:
        coro_func: Async function to execute
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        backoff_multiplier: Multiplier for backoff time
        max_backoff: Maximum backoff time in seconds
        retryable_exceptions: Tuple of exceptions to retry on
        
    Returns:
        Result from successful execution
        
    Raises:
        Last exception encountered if all retries fail
    """
    backoff = initial_backoff
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            return await coro_func()
        except retryable_exceptions as e:
            last_error = e
            if attempt < max_retries:
                await asyncio.sleep(backoff)
                backoff = min(backoff * backoff_multiplier, max_backoff)
                continue
            raise
        except Exception as e:
            # Non-retryable exception
            raise
    
    if last_error:
        raise last_error


# ---------------------------
# OpenRouter Client
# ---------------------------

class OpenRouterClient:
    """
    Async httpx-based client for OpenRouter API with session reuse.
    
    Usage:
        async with OpenRouterClient(api_key="...", model="gpt-4") as client:
            response = await client.chat(prompt="Hello!")
            
        # Or manual management:
        client = OpenRouterClient(api_key="...", model="gpt-4")
        await client.__aenter__()
        try:
            response = await client.chat(prompt="Hello!")
        finally:
            await client.__aexit__(None, None, None)
    """
    
    DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RETRIES = 2
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        api_url: str = None,
        timeout: float = None,
        max_retries: int = None,
        headers: Optional[Dict[str, str]] = None,
        trust_env: bool = True,
    ):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            model: Model identifier (default: gpt-4o-mini)
            api_url: API endpoint URL (default: OpenRouter chat completions)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 2)
            headers: Additional headers to include in requests
            trust_env: Whether to respect proxy environment variables
        """
        self.api_key = api_key
        self.model = model
        self.api_url = api_url or self.DEFAULT_API_URL
        self.timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else self.DEFAULT_MAX_RETRIES
        self.trust_env = trust_env
        
        self._base_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        if headers:
            self._base_headers.update(headers)
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            trust_env=self.trust_env
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager and cleanup."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _validate_client(self):
        """Ensure client is initialized."""
        if self._client is None:
            raise RuntimeError(
                "Client not initialized. Use 'async with OpenRouterClient(...)' "
                "or call __aenter__() before making requests."
            )
    
    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build request payload for OpenRouter API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional parameters for the API
            
        Returns:
            Complete payload dictionary
        """
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        if temperature is not None:
            payload["temperature"] = temperature
        
        payload.update(kwargs)
        
        return payload
    
    async def _make_request(
        self,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> OpenRouterResponse:
        """
        Make a single request to OpenRouter API with error handling.
        
        Args:
            payload: Request payload
            headers: Optional additional headers
            
        Returns:
            OpenRouterResponse object
            
        Raises:
            Various OpenRouterError subclasses on failure
        """
        self._validate_client()
        
        request_headers = self._base_headers.copy()
        if headers:
            request_headers.update(headers)
        
        start_time = time.time()
        
        try:
            async def do_request():
                response = await self._client.post(
                    self.api_url,
                    headers=request_headers,
                    json=payload
                )
                response.raise_for_status()
                return response
            
            # Execute with exponential backoff retry
            response = await exponential_backoff_retry(
                do_request,
                max_retries=self.max_retries
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            data = response.json()
            content = extract_content_from_response(data)
            
            return OpenRouterResponse(
                content=content,
                model=self.model,
                success=True,
                latency_ms=round(latency_ms, 2),
                raw_response=data,
            )
            
        except httpx.ConnectError as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            if "getaddrinfo failed" in error_msg or "11001" in error_msg:
                error = (
                    f"Network error: Cannot connect to OpenRouter API. "
                    f"Please check your internet connection, proxy settings, or firewall. "
                    f"URL: {self.api_url}"
                )
                raise OpenRouterConnectionError(error) from e
            
            error = f"Failed to connect to OpenRouter API: {error_msg}"
            raise OpenRouterConnectionError(error) from e
            
        except httpx.HTTPStatusError as e:
            latency_ms = (time.time() - start_time) * 1000
            
            if e.response.status_code == 401:
                error = "Invalid API key. Please check your OpenRouter API key."
                raise OpenRouterAuthenticationError(error) from e
            elif e.response.status_code == 429:
                error = "Rate limit exceeded. Please try again later."
                raise OpenRouterRateLimitError(error) from e
            else:
                error = f"HTTP error {e.response.status_code}: {e.response.text}"
                raise OpenRouterAPIError(error) from e
        
        except OpenRouterParsingError as e:
            latency_ms = (time.time() - start_time) * 1000
            return OpenRouterResponse(
                content="",
                model=self.model,
                success=False,
                latency_ms=round(latency_ms, 2),
                error=str(e),
            )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error = f"Unexpected error: {str(e)}"
            
            return OpenRouterResponse(
                content="",
                model=self.model,
                success=False,
                latency_ms=round(latency_ms, 2),
                error=error,
            )
    
    async def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        parse_json: bool = False,
        **kwargs
    ) -> OpenRouterResponse:
        """
        Send a chat prompt to OpenRouter API.
        
        Args:
            prompt: User prompt text
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            parse_json: Whether to attempt JSON parsing of response
            **kwargs: Additional parameters for the API
            
        Returns:
            OpenRouterResponse object with result
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = self._build_payload(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        response = await self._make_request(payload)
        
        if response.success and parse_json and response.content:
            try:
                response.parsed_json = extract_json_from_text(response.content)
            except OpenRouterParsingError as e:
                response.success = False
                response.error = f"JSON parsing failed: {str(e)}"
        
        return response
    
    async def chat_many(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        parse_json: bool = False,
        **kwargs
    ) -> List[OpenRouterResponse]:
        """
        Send multiple prompts concurrently to OpenRouter API.
        
        Args:
            prompts: List of user prompt texts
            system_prompt: Optional system prompt (applied to all)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            parse_json: Whether to attempt JSON parsing of responses
            **kwargs: Additional parameters for the API
            
        Returns:
            List of OpenRouterResponse objects in same order as prompts
        """
        tasks = [
            self.chat(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                parse_json=parse_json,
                **kwargs
            )
            for prompt in prompts
        ]
        
        return await asyncio.gather(*tasks)
    
    async def custom_request(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        parse_json: bool = False,
        **kwargs
    ) -> OpenRouterResponse:
        """
        Make a custom request with full control over messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 to 2.0)
            parse_json: Whether to attempt JSON parsing of response
            **kwargs: Additional parameters for the API
            
        Returns:
            OpenRouterResponse object with result
        """
        payload = self._build_payload(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        response = await self._make_request(payload)
        
        if response.success and parse_json and response.content:
            try:
                response.parsed_json = extract_json_from_text(response.content)
            except OpenRouterParsingError as e:
                response.success = False
                response.error = f"JSON parsing failed: {str(e)}"
        
        return response


# ---------------------------
# Convenience Functions
# ---------------------------

async def simple_chat(
    api_key: str,
    prompt: str,
    model: str = "gpt-4o-mini",
    system_prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    parse_json: bool = False,
    **kwargs
) -> OpenRouterResponse:
    """
    Convenience function for a single chat request without manual client management.
    
    Args:
        api_key: OpenRouter API key
        prompt: User prompt text
        model: Model identifier
        system_prompt: Optional system prompt
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        parse_json: Whether to attempt JSON parsing of response
        **kwargs: Additional parameters
        
    Returns:
        OpenRouterResponse object
    """
    async with OpenRouterClient(api_key=api_key, model=model) as client:
        return await client.chat(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            parse_json=parse_json,
            **kwargs
        )


async def batch_chat(
    api_key: str,
    prompts: List[str],
    model: str = "gpt-4o-mini",
    system_prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    parse_json: bool = False,
    **kwargs
) -> List[OpenRouterResponse]:
    """
    Convenience function for multiple concurrent chat requests.
    
    Args:
        api_key: OpenRouter API key
        prompts: List of user prompt texts
        model: Model identifier
        system_prompt: Optional system prompt
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        parse_json: Whether to attempt JSON parsing of responses
        **kwargs: Additional parameters
        
    Returns:
        List of OpenRouterResponse objects
    """
    async with OpenRouterClient(api_key=api_key, model=model) as client:
        return await client.chat_many(
            prompts=prompts,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            parse_json=parse_json,
            **kwargs
        )
