"""Simple async test to verify pytest-asyncio."""
import asyncio
import pytest

pytestmark = pytest.mark.asyncio

async def test_async():
    """Simple async test that should pass."""
    print("Async test is running!")
    await asyncio.sleep(0.1)
    assert 1 + 1 == 2
