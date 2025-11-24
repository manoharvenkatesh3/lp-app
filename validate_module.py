#!/usr/bin/env python3
"""
Validation script for openrouter_client module.
Runs various checks to ensure the module is properly implemented.
"""

import sys
import importlib.util
import inspect


def check_module_imports():
    """Check if module can be imported."""
    print("✓ Checking module imports...")
    try:
        import openrouter_client
        return True, "Module imported successfully"
    except Exception as e:
        return False, f"Import failed: {e}"


def check_required_classes():
    """Check if all required classes are present."""
    print("✓ Checking required classes...")
    import openrouter_client
    
    required_classes = [
        'OpenRouterClient',
        'OpenRouterResponse',
        'OpenRouterError',
        'OpenRouterConnectionError',
        'OpenRouterAuthenticationError',
        'OpenRouterRateLimitError',
        'OpenRouterAPIError',
        'OpenRouterParsingError',
    ]
    
    missing = []
    for cls_name in required_classes:
        if not hasattr(openrouter_client, cls_name):
            missing.append(cls_name)
    
    if missing:
        return False, f"Missing classes: {', '.join(missing)}"
    return True, f"All {len(required_classes)} required classes present"


def check_required_functions():
    """Check if all required functions are present."""
    print("✓ Checking required functions...")
    import openrouter_client
    
    required_functions = [
        'extract_json_from_text',
        'extract_content_from_response',
        'exponential_backoff_retry',
        'simple_chat',
        'batch_chat',
    ]
    
    missing = []
    for func_name in required_functions:
        if not hasattr(openrouter_client, func_name):
            missing.append(func_name)
    
    if missing:
        return False, f"Missing functions: {', '.join(missing)}"
    return True, f"All {len(required_functions)} required functions present"


def check_client_methods():
    """Check if OpenRouterClient has required methods."""
    print("✓ Checking OpenRouterClient methods...")
    import openrouter_client
    
    required_methods = [
        '__aenter__',
        '__aexit__',
        'chat',
        'chat_many',
        'custom_request',
    ]
    
    client_class = openrouter_client.OpenRouterClient
    missing = []
    
    for method_name in required_methods:
        if not hasattr(client_class, method_name):
            missing.append(method_name)
    
    if missing:
        return False, f"Missing methods: {', '.join(missing)}"
    return True, f"All {len(required_methods)} required methods present"


def check_response_attributes():
    """Check if OpenRouterResponse has required attributes."""
    print("✓ Checking OpenRouterResponse attributes...")
    import openrouter_client
    
    required_attrs = [
        'content',
        'model',
        'success',
        'latency_ms',
        'timestamp',
        'error',
        'raw_response',
        'parsed_json',
    ]
    
    # Create a dummy response to check attributes
    response = openrouter_client.OpenRouterResponse(
        content="test",
        model="test-model",
        success=True,
        latency_ms=100.0
    )
    
    missing = []
    for attr_name in required_attrs:
        if not hasattr(response, attr_name):
            missing.append(attr_name)
    
    if missing:
        return False, f"Missing attributes: {', '.join(missing)}"
    return True, f"All {len(required_attrs)} required attributes present"


def check_async_support():
    """Check if client supports async context manager."""
    print("✓ Checking async context manager support...")
    import openrouter_client
    import asyncio
    
    client = openrouter_client.OpenRouterClient(api_key="test-key")
    
    # Check if __aenter__ and __aexit__ are coroutines
    if not asyncio.iscoroutinefunction(client.__aenter__):
        return False, "__aenter__ is not a coroutine"
    if not asyncio.iscoroutinefunction(client.__aexit__):
        return False, "__aexit__ is not a coroutine"
    
    return True, "Async context manager properly implemented"


def check_docstrings():
    """Check if main components have docstrings."""
    print("✓ Checking documentation...")
    import openrouter_client
    
    components_to_check = [
        ('Module', openrouter_client),
        ('OpenRouterClient', openrouter_client.OpenRouterClient),
        ('OpenRouterResponse', openrouter_client.OpenRouterResponse),
        ('chat', openrouter_client.OpenRouterClient.chat),
        ('extract_json_from_text', openrouter_client.extract_json_from_text),
    ]
    
    missing_docs = []
    for name, component in components_to_check:
        if not component.__doc__ or len(component.__doc__.strip()) < 10:
            missing_docs.append(name)
    
    if missing_docs:
        return False, f"Missing/insufficient docstrings: {', '.join(missing_docs)}"
    return True, f"All {len(components_to_check)} checked components have docstrings"


def check_test_file():
    """Check if test file exists and is valid."""
    print("✓ Checking test file...")
    try:
        spec = importlib.util.spec_from_file_location("test_openrouter_client", "test_openrouter_client.py")
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # Count test classes and functions
        test_classes = sum(1 for name in dir(test_module) if name.startswith('Test'))
        test_functions = sum(1 for name, obj in inspect.getmembers(test_module, inspect.isfunction) 
                           if name.startswith('test_'))
        
        total_tests = test_classes + test_functions
        
        if test_classes < 3:
            return False, f"Only {test_classes} test classes found (expected at least 3)"
        
        return True, f"Test file valid with {test_classes} test classes and {test_functions} test functions"
    except Exception as e:
        return False, f"Test file validation failed: {e}"


def check_example_file():
    """Check if example file exists."""
    print("✓ Checking example file...")
    try:
        with open('example_openrouter_usage.py', 'r') as f:
            content = f.read()
            if 'async def' not in content:
                return False, "No async functions found in example file"
            if 'OpenRouterClient' not in content:
                return False, "OpenRouterClient not used in example file"
        return True, "Example file present and valid"
    except Exception as e:
        return False, f"Example file check failed: {e}"


def check_documentation_files():
    """Check if documentation files exist."""
    print("✓ Checking documentation files...")
    
    required_docs = [
        'OPENROUTER_CLIENT_README.md',
        'INTEGRATION_GUIDE.md',
        'DELIVERABLES.md',
    ]
    
    missing = []
    for doc in required_docs:
        try:
            with open(doc, 'r') as f:
                content = f.read()
                if len(content) < 100:
                    missing.append(f"{doc} (too short)")
        except FileNotFoundError:
            missing.append(doc)
    
    if missing:
        return False, f"Missing/insufficient documentation: {', '.join(missing)}"
    return True, f"All {len(required_docs)} documentation files present"


def check_gitignore():
    """Check if .gitignore exists."""
    print("✓ Checking .gitignore...")
    try:
        with open('.gitignore', 'r') as f:
            content = f.read()
            required_patterns = ['__pycache__', '.venv', '.env']
            missing = [p for p in required_patterns if p not in content]
            if missing:
                return False, f"Missing patterns in .gitignore: {', '.join(missing)}"
        return True, ".gitignore present with required patterns"
    except FileNotFoundError:
        return False, ".gitignore file not found"


def run_all_checks():
    """Run all validation checks."""
    print("=" * 60)
    print("OpenRouter Client Module Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("Module Imports", check_module_imports),
        ("Required Classes", check_required_classes),
        ("Required Functions", check_required_functions),
        ("Client Methods", check_client_methods),
        ("Response Attributes", check_response_attributes),
        ("Async Support", check_async_support),
        ("Documentation", check_docstrings),
        ("Test File", check_test_file),
        ("Example File", check_example_file),
        ("Documentation Files", check_documentation_files),
        (".gitignore", check_gitignore),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        try:
            success, message = check_func()
            results.append((check_name, success, message))
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            results.append((check_name, False, f"Check crashed: {e}"))
            failed += 1
        print()
    
    # Print results
    print("=" * 60)
    print("Validation Results")
    print("=" * 60)
    print()
    
    for check_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {check_name}")
        print(f"       {message}")
        print()
    
    print("=" * 60)
    print(f"Summary: {passed} passed, {failed} failed out of {len(checks)} checks")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All validation checks passed! Module is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {failed} validation check(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_checks())
