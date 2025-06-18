"""Simple async test to verify pytest-asyncio is working."""
import pytest
import asyncio

# This marker enables async test support for all tests in this module
pytestmark = pytest.mark.asyncio

async def test_simple_async():
    """Simple async test that should pass."""
    print("This is an async test!")
    await asyncio.sleep(0.1)
    assert 1 + 1 == 2
