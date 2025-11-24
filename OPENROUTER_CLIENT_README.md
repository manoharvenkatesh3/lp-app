# OpenRouter Client

A robust async httpx-based client for the OpenRouter API with comprehensive error handling, retry logic, and concurrent request support.

## Features

- ✅ **Session-level AsyncClient reuse** for efficient connection management
- ✅ **Configurable headers** (API key, model, custom headers)
- ✅ **Structured request payloads** with flexible parameter support
- ✅ **Exponential backoff retries** with configurable retry limits
- ✅ **Timeout handling** with customizable timeout values
- ✅ **JSON-formatted response parsing** with automatic extraction
- ✅ **Concurrent request support** via `asyncio.gather`
- ✅ **Standardized result objects** with metadata (model, latency, errors)
- ✅ **Graceful fallbacks** for API failures with user-friendly error messages
- ✅ **Unit-testable design** with helper functions isolated from API logic

## Installation

The module requires the following dependencies:

```bash
pip install httpx>=0.24.0
```

## Quick Start

### Basic Usage

```python
import asyncio
from openrouter_client import OpenRouterClient

async def main():
    api_key = "your-openrouter-api-key"
    
    async with OpenRouterClient(api_key=api_key, model="gpt-4o-mini") as client:
        response = await client.chat(
            prompt="What is the capital of France?",
            max_tokens=50,
            temperature=0.0
        )
        
        if response.success:
            print(f"Response: {response.content}")
            print(f"Latency: {response.latency_ms}ms")
        else:
            print(f"Error: {response.error}")

asyncio.run(main())
```

### Convenience Functions

For simple use cases, use the convenience functions:

```python
from openrouter_client import simple_chat

response = await simple_chat(
    api_key="your-api-key",
    prompt="Hello, world!",
    model="gpt-4o-mini"
)
```

## API Reference

### OpenRouterClient

Main client class for interacting with OpenRouter API.

#### Initialization

```python
client = OpenRouterClient(
    api_key: str,                    # Required: OpenRouter API key
    model: str = "gpt-4o-mini",      # Model identifier
    api_url: str = None,             # API endpoint (default: OpenRouter)
    timeout: float = 30.0,           # Request timeout in seconds
    max_retries: int = 2,            # Maximum retry attempts
    headers: Dict[str, str] = None,  # Additional headers
    trust_env: bool = True,          # Respect proxy env variables
)
```

#### Methods

##### `chat()`

Send a single chat prompt.

```python
response = await client.chat(
    prompt: str,                     # User prompt
    system_prompt: str = None,       # Optional system prompt
    max_tokens: int = None,          # Max tokens in response
    temperature: float = None,       # Sampling temperature (0.0-2.0)
    parse_json: bool = False,        # Auto-parse JSON response
    **kwargs                         # Additional API parameters
)
```

##### `chat_many()`

Send multiple prompts concurrently.

```python
responses = await client.chat_many(
    prompts: List[str],              # List of user prompts
    system_prompt: str = None,       # Optional system prompt (all prompts)
    max_tokens: int = None,
    temperature: float = None,
    parse_json: bool = False,
    **kwargs
)
```

##### `custom_request()`

Make a request with full control over message structure.

```python
response = await client.custom_request(
    messages: List[Dict[str, str]],  # Custom message list
    max_tokens: int = None,
    temperature: float = None,
    parse_json: bool = False,
    **kwargs
)
```

### OpenRouterResponse

Response object returned by all client methods.

#### Attributes

```python
@dataclass
class OpenRouterResponse:
    content: str                     # Response text content
    model: str                       # Model used
    success: bool                    # Whether request succeeded
    latency_ms: float                # Request latency in milliseconds
    timestamp: datetime              # Response timestamp
    error: Optional[str]             # Error message if failed
    raw_response: Optional[Dict]     # Raw API response
    parsed_json: Optional[Dict]      # Parsed JSON (if parse_json=True)
```

#### Methods

```python
response.to_dict()  # Convert to dictionary format
```

### Convenience Functions

#### `simple_chat()`

One-off chat request without manual client management.

```python
response = await simple_chat(
    api_key: str,
    prompt: str,
    model: str = "gpt-4o-mini",
    system_prompt: str = None,
    max_tokens: int = None,
    temperature: float = None,
    parse_json: bool = False,
    **kwargs
)
```

#### `batch_chat()`

Multiple concurrent requests without manual client management.

```python
responses = await batch_chat(
    api_key: str,
    prompts: List[str],
    model: str = "gpt-4o-mini",
    system_prompt: str = None,
    max_tokens: int = None,
    temperature: float = None,
    parse_json: bool = False,
    **kwargs
)
```

### Helper Functions

#### `extract_json_from_text()`

Extract and parse JSON from text containing other content.

```python
from openrouter_client import extract_json_from_text

text = 'Here is the data: {"key": "value"} and more text'
json_obj = extract_json_from_text(text)  # Returns: {"key": "value"}
```

#### `extract_content_from_response()`

Extract text content from various OpenRouter response formats.

```python
from openrouter_client import extract_content_from_response

content = extract_content_from_response(api_response_dict)
```

## Error Handling

The module provides specific exception types for different failure scenarios:

```python
from openrouter_client import (
    OpenRouterError,               # Base exception
    OpenRouterConnectionError,     # Network/connection issues
    OpenRouterAuthenticationError, # Invalid API key
    OpenRouterRateLimitError,      # Rate limit exceeded
    OpenRouterAPIError,            # General API errors
    OpenRouterParsingError,        # Response parsing failures
)

try:
    async with OpenRouterClient(api_key=api_key) as client:
        response = await client.chat(prompt="Hello")
except OpenRouterAuthenticationError:
    print("Invalid API key")
except OpenRouterConnectionError:
    print("Network connection failed")
except OpenRouterRateLimitError:
    print("Rate limit exceeded, try again later")
except OpenRouterError as e:
    print(f"OpenRouter error: {e}")
```

## Advanced Usage

### Multi-turn Conversations

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Nice to meet you, Alice!"},
    {"role": "user", "content": "What's my name?"}
]

response = await client.custom_request(messages=messages)
```

### JSON Response Parsing

```python
response = await client.chat(
    prompt="Return JSON with keys 'status' and 'message'",
    system_prompt="Respond only with valid JSON",
    parse_json=True
)

if response.success and response.parsed_json:
    print(response.parsed_json)  # Automatically parsed dict
```

### Concurrent Requests

```python
prompts = [
    "What is 2+2?",
    "What is the capital of France?",
    "Name a programming language."
]

responses = await client.chat_many(prompts=prompts)

for prompt, response in zip(prompts, responses):
    if response.success:
        print(f"Q: {prompt}")
        print(f"A: {response.content}\n")
```

### Custom Configuration

```python
client = OpenRouterClient(
    api_key="your-key",
    model="gpt-4",
    timeout=60.0,              # 60 second timeout
    max_retries=5,             # 5 retry attempts
    headers={                  # Custom headers
        "X-Custom-Header": "value"
    }
)
```

## Testing

The module is designed to be easily testable. Helper functions are pure and stateless, making unit testing straightforward.

Run the included tests:

```bash
pytest test_openrouter_client.py -v
```

### Example Test

```python
from openrouter_client import extract_json_from_text

def test_extract_json():
    text = 'Result: {"status": "ok"}'
    result = extract_json_from_text(text)
    assert result == {"status": "ok"}
```

## Integration with Existing Code

The module is designed to be a drop-in replacement or enhancement for existing OpenRouter API calls. It can coexist with existing implementations and be gradually adopted.

### Migrating from Direct httpx Calls

**Before:**
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]}
    )
    data = response.json()
```

**After:**
```python
async with OpenRouterClient(api_key=api_key, model="gpt-4") as client:
    response = await client.chat(prompt="Hello")
```

## Best Practices

1. **Use context manager**: Always use `async with` to ensure proper cleanup
2. **Reuse client**: For multiple requests, create one client and reuse it
3. **Handle errors gracefully**: Check `response.success` and handle errors
4. **Set appropriate timeouts**: Adjust based on your use case
5. **Use batch requests**: For multiple prompts, use `chat_many()` for better performance
6. **Monitor latency**: Use `response.latency_ms` for performance tracking

## Environment Variables

The client respects standard HTTP proxy environment variables when `trust_env=True` (default):

- `HTTP_PROXY`
- `HTTPS_PROXY`
- `NO_PROXY`

## License

This module is provided as-is for use with the OpenRouter API.

## Support

For issues or questions about this client, refer to the test suite and examples for guidance.
For OpenRouter API issues, consult the [OpenRouter documentation](https://openrouter.ai/docs).
