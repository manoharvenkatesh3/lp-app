# Integration Guide: OpenRouter Client

This guide shows how to integrate the new `openrouter_client.py` module with the existing `streamlit_app.py` application.

## Overview

The `openrouter_client.py` module provides a cleaner, more robust alternative to the existing OpenRouter API calls in `streamlit_app.py`. It can be integrated gradually or used as a complete replacement.

## Current Implementation in streamlit_app.py

The current implementation has a `call_openrouter()` function (lines 624-698) that:
- Makes direct httpx calls
- Implements retry logic with exponential backoff
- Handles various error cases
- Extracts JSON from responses

## Benefits of Using the New Client

1. **Better separation of concerns**: API logic is isolated in its own module
2. **Enhanced testability**: Unit tests can mock the client easily
3. **Reusable**: Can be used across multiple parts of the application
4. **Type safety**: Structured response objects with clear attributes
5. **Better error handling**: Specific exception types for different failures
6. **Metadata tracking**: Built-in latency and timestamp tracking
7. **Concurrent support**: Easy batch processing with `chat_many()`

## Option 1: Minimal Integration (Recommended)

Replace the existing `call_openrouter()` function with the new client:

### Step 1: Add import at the top of streamlit_app.py

```python
from openrouter_client import OpenRouterClient, OpenRouterError
```

### Step 2: Replace the call_openrouter function

**Replace this (lines 624-698):**

```python
async def call_openrouter(program_text: str, retries: int = 2, timeout: int = 30) -> Dict[str, Any]:
    # ... existing implementation ...
```

**With this:**

```python
async def call_openrouter(program_text: str, retries: int = 2, timeout: int = 30) -> Dict[str, Any]:
    """
    Calls OpenRouter chat completions and returns the parsed JSON LLM payload.
    Now uses the openrouter_client module for better reliability.
    """
    try:
        async with OpenRouterClient(
            api_key=OPENROUTER_KEY,
            model=OPENROUTER_MODEL,
            timeout=timeout,
            max_retries=retries
        ) as client:
            response = await client.chat(
                prompt=LLM_USER_PROMPT_TEMPLATE.format(program_text=program_text),
                system_prompt=LLM_SYSTEM_PROMPT,
                max_tokens=800,
                temperature=0.0,
                parse_json=True
            )
            
            if not response.success:
                raise ValueError(response.error or "Unknown error occurred")
            
            if response.parsed_json:
                return response.parsed_json
            else:
                raise ValueError("Failed to parse JSON from response")
                
    except OpenRouterError as e:
        # Re-raise with original error messages for backward compatibility
        raise ValueError(str(e)) from e
    except Exception as e:
        raise
```

### Step 3: Test the integration

Run the Streamlit app to ensure everything works:

```bash
streamlit run streamlit_app.py
```

## Option 2: Enhanced Integration (Advanced)

For more advanced features, you can enhance the application to use multiple concurrent requests.

### Example: Batch Analysis

If you want to analyze multiple programs concurrently:

```python
async def analyze_multiple_programs(program_texts: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze multiple loyalty programs concurrently.
    """
    async with OpenRouterClient(
        api_key=OPENROUTER_KEY,
        model=OPENROUTER_MODEL,
        timeout=30,
        max_retries=2
    ) as client:
        prompts = [
            LLM_USER_PROMPT_TEMPLATE.format(program_text=text)
            for text in program_texts
        ]
        
        responses = await client.chat_many(
            prompts=prompts,
            system_prompt=LLM_SYSTEM_PROMPT,
            max_tokens=800,
            temperature=0.0,
            parse_json=True
        )
        
        results = []
        for response in responses:
            if response.success and response.parsed_json:
                results.append(response.parsed_json)
            else:
                results.append({"error": response.error})
        
        return results
```

## Option 3: Gradual Migration

You can keep both implementations and gradually migrate:

1. Keep the existing `call_openrouter()` function
2. Add new functions using the client: `call_openrouter_v2()`
3. Test the new implementation in parallel
4. Switch over when confident
5. Remove the old implementation

## Error Handling Comparison

### Old Implementation

```python
try:
    result = await call_openrouter(program_text)
except ConnectionError as e:
    st.error(f"Connection error: {e}")
except ValueError as e:
    st.error(f"API error: {e}")
```

### New Implementation

```python
from openrouter_client import (
    OpenRouterConnectionError,
    OpenRouterAuthenticationError,
    OpenRouterRateLimitError,
)

try:
    result = await call_openrouter(program_text)
except OpenRouterAuthenticationError:
    st.error("Invalid API key. Please check your configuration.")
except OpenRouterRateLimitError:
    st.error("Rate limit exceeded. Please wait and try again.")
except OpenRouterConnectionError as e:
    st.error(f"Network error: {e}")
except Exception as e:
    st.error(f"Unexpected error: {e}")
```

## Performance Benefits

### Single Request

No significant performance difference for single requests.

### Multiple Requests

For analyzing multiple programs or making multiple API calls:

**Before (sequential):**
```python
results = []
for program in programs:
    result = await call_openrouter(program)
    results.append(result)
# Total time: ~3s per request × N requests
```

**After (concurrent):**
```python
async with OpenRouterClient(...) as client:
    results = await client.chat_many(prompts)
# Total time: ~3s (all requests in parallel)
```

## Testing Benefits

### Old Implementation

Testing required mocking httpx directly:

```python
@pytest.mark.asyncio
async def test_call_openrouter():
    with patch('httpx.AsyncClient.post') as mock_post:
        # Complex mocking setup...
        result = await call_openrouter("test")
```

### New Implementation

Testing is much cleaner:

```python
@pytest.mark.asyncio
async def test_with_new_client():
    mock_response = OpenRouterResponse(
        content='{"test": "data"}',
        model="gpt-4",
        success=True,
        latency_ms=100.0
    )
    
    async with OpenRouterClient(api_key="test") as client:
        with patch.object(client, '_make_request', return_value=mock_response):
            response = await client.chat("test", parse_json=True)
            assert response.parsed_json == {"test": "data"}
```

## Configuration

The client respects the same configuration variables:

```python
# In .streamlit/secrets.toml
OPENROUTER_API_KEY = "your-key-here"
OPENROUTER_MODEL = "gpt-4o-mini"
```

Access in code:
```python
import streamlit as st

OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", "gpt-4o-mini")
```

## Migration Checklist

- [ ] Add `openrouter_client.py` to project
- [ ] Add import to `streamlit_app.py`
- [ ] Create backup of current `call_openrouter()` function
- [ ] Replace implementation with new client
- [ ] Test with sample loyalty program data
- [ ] Verify error handling works correctly
- [ ] Test with invalid API key (should fail gracefully)
- [ ] Test with network disconnected (should show appropriate error)
- [ ] Update any documentation
- [ ] Remove old implementation once confident

## Rollback Plan

If you need to rollback:

1. The old `call_openrouter()` function is preserved in this guide
2. Simply replace the new implementation with the old one
3. Remove the import of `openrouter_client`
4. The module can remain in the project without affecting anything

## Support

For issues with the OpenRouter client module:
- Check the test suite in `test_openrouter_client.py`
- Review examples in `example_openrouter_usage.py`
- Read the full documentation in `OPENROUTER_CLIENT_README.md`

## Summary

The new `openrouter_client.py` module provides a production-ready, well-tested interface to the OpenRouter API. It's designed to be a drop-in replacement for the existing implementation while providing additional features and better maintainability.

**Recommended approach**: Start with Option 1 (Minimal Integration) for a safe, backward-compatible upgrade.
