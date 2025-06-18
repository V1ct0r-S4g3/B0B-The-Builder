"""
Pytest configuration and fixtures for testing.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def pytest_configure(config):
    """Pytest configuration hook."""
    # Set environment variables for testing
    os.environ["PYTHONPATH"] = str(project_root) + os.pathsep + os.environ.get("PYTHONPATH", "")
