"""
Example usage of openrouter_client module.

Demonstrates various features:
- Basic chat requests
- Concurrent batch requests
- JSON parsing
- Error handling
- Custom request messages
"""

import asyncio
from openrouter_client import (
    OpenRouterClient,
    simple_chat,
    batch_chat,
    OpenRouterError,
    OpenRouterConnectionError,
    OpenRouterAuthenticationError,
)


async def example_basic_chat():
    """Example 1: Basic chat request with context manager."""
    print("\n=== Example 1: Basic Chat ===")
    
    api_key = "your-api-key-here"
    
    async with OpenRouterClient(api_key=api_key, model="gpt-4o-mini") as client:
        response = await client.chat(
            prompt="What is the capital of France?",
            max_tokens=50,
            temperature=0.0
        )
        
        if response.success:
            print(f"Response: {response.content}")
            print(f"Latency: {response.latency_ms}ms")
            print(f"Model: {response.model}")
        else:
            print(f"Error: {response.error}")


async def example_chat_with_system_prompt():
    """Example 2: Chat with system prompt."""
    print("\n=== Example 2: Chat with System Prompt ===")
    
    api_key = "your-api-key-here"
    
    async with OpenRouterClient(api_key=api_key) as client:
        response = await client.chat(
            prompt="Give me a programming tip",
            system_prompt="You are a senior software engineer who gives concise advice.",
            max_tokens=100,
            temperature=0.7
        )
        
        if response.success:
            print(f"Tip: {response.content}")


async def example_json_parsing():
    """Example 3: Request with JSON parsing."""
    print("\n=== Example 3: JSON Parsing ===")
    
    api_key = "your-api-key-here"
    
    async with OpenRouterClient(api_key=api_key) as client:
        response = await client.chat(
            prompt="Return a JSON object with keys 'name' and 'age' for a fictional character.",
            system_prompt="You must respond with valid JSON only, no other text.",
            max_tokens=100,
            temperature=0.0,
            parse_json=True
        )
        
        if response.success:
            print(f"Parsed JSON: {response.parsed_json}")
        else:
            print(f"Error: {response.error}")


async def example_concurrent_requests():
    """Example 4: Multiple concurrent requests."""
    print("\n=== Example 4: Concurrent Batch Requests ===")
    
    api_key = "your-api-key-here"
    
    prompts = [
        "What is 2+2?",
        "What is the capital of Japan?",
        "Name a programming language.",
    ]
    
    async with OpenRouterClient(api_key=api_key) as client:
        responses = await client.chat_many(
            prompts=prompts,
            max_tokens=20,
            temperature=0.0
        )
        
        for i, response in enumerate(responses):
            if response.success:
                print(f"Q{i+1}: {prompts[i]}")
                print(f"A{i+1}: {response.content}")
                print(f"Latency: {response.latency_ms}ms\n")


async def example_custom_messages():
    """Example 5: Custom multi-turn conversation."""
    print("\n=== Example 5: Custom Multi-Turn Conversation ===")
    
    api_key = "your-api-key-here"
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "My name is Alice."},
        {"role": "assistant", "content": "Nice to meet you, Alice! How can I help you today?"},
        {"role": "user", "content": "What's my name?"}
    ]
    
    async with OpenRouterClient(api_key=api_key) as client:
        response = await client.custom_request(
            messages=messages,
            max_tokens=50,
            temperature=0.0
        )
        
        if response.success:
            print(f"Assistant: {response.content}")


async def example_error_handling():
    """Example 6: Graceful error handling."""
    print("\n=== Example 6: Error Handling ===")
    
    api_key = "invalid-key"
    
    try:
        async with OpenRouterClient(api_key=api_key) as client:
            response = await client.chat(prompt="Hello")
            
            if not response.success:
                print(f"Request failed: {response.error}")
                
    except OpenRouterAuthenticationError as e:
        print(f"Authentication failed: {e}")
    except OpenRouterConnectionError as e:
        print(f"Connection failed: {e}")
    except OpenRouterError as e:
        print(f"OpenRouter error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


async def example_convenience_functions():
    """Example 7: Using convenience functions."""
    print("\n=== Example 7: Convenience Functions ===")
    
    api_key = "your-api-key-here"
    
    # Simple single request
    response = await simple_chat(
        api_key=api_key,
        prompt="Say hello",
        max_tokens=20
    )
    
    if response.success:
        print(f"Simple chat: {response.content}")
    
    # Batch request
    responses = await batch_chat(
        api_key=api_key,
        prompts=["Hi", "Hello", "Hey there"],
        max_tokens=20
    )
    
    print(f"\nBatch results: {len(responses)} responses")
    for i, r in enumerate(responses):
        if r.success:
            print(f"  {i+1}. {r.content[:30]}...")


async def example_response_metadata():
    """Example 8: Accessing response metadata."""
    print("\n=== Example 8: Response Metadata ===")
    
    api_key = "your-api-key-here"
    
    async with OpenRouterClient(api_key=api_key, model="gpt-4o-mini") as client:
        response = await client.chat(prompt="Hello")
        
        if response.success:
            metadata = response.to_dict()
            print(f"Full metadata:")
            for key, value in metadata.items():
                if key != "content":
                    print(f"  {key}: {value}")


async def main():
    """Run all examples."""
    print("OpenRouter Client Examples")
    print("=" * 50)
    
    # Note: Replace "your-api-key-here" with actual API key to run
    print("\nNote: These examples require a valid OpenRouter API key.")
    print("Set your API key in the example functions to run them.\n")
    
    # Uncomment the examples you want to run:
    
    # await example_basic_chat()
    # await example_chat_with_system_prompt()
    # await example_json_parsing()
    # await example_concurrent_requests()
    # await example_custom_messages()
    # await example_error_handling()
    # await example_convenience_functions()
    # await example_response_metadata()


if __name__ == "__main__":
    asyncio.run(main())
