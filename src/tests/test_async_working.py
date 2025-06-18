"""Test file to verify async tests work with pytest."""
import pytest

@pytest.mark.asyncio
async def test_async_working():
    """Simple async test to verify pytest-asyncio is working."""
    print("Async test is running")
    result = await async_function()
    assert result == "success"

async def async_function():
    """Simple async function for testing."""
    return "success"
