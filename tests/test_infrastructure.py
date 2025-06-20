"""
Test infrastructure verification for the SC2 Bot project.

This module contains tests to verify that the test infrastructure is working correctly.
"""
import unittest
import os
import sys
import importlib
from pathlib import Path

class TestInfrastructure(unittest.TestCase):
    """Test cases for verifying the test infrastructure."""

    def test_import_bot_module(self):
        """Test that the main bot module can be imported."""
        try:
            import src.bot
            self.assertTrue(True, "Successfully imported src.bot")
        except ImportError as e:
            self.fail(f"Failed to import src.bot: {e}")

    def test_import_managers(self):
        """Test that all manager modules can be imported."""
        managers = [
            'economy_manager',
            'military_manager',
            'head_manager'
        ]
        
        for manager in managers:
            with self.subTest(manager=manager):
                try:
                    module = importlib.import_module(f'src.managers.{manager}')
                    self.assertIsNotNone(module, f"Failed to import {manager}")
                except ImportError as e:
                    self.fail(f"Failed to import {manager}: {e}")

    def test_project_structure(self):
        """Verify that the project has the expected directory structure."""
        project_root = Path(__file__).parent.parent
        expected_dirs = [
            'src',
            'src/managers',
            'tests',
            'config'
        ]
        
        for dir_path in expected_dirs:
            full_path = project_root / dir_path
            with self.subTest(directory=dir_path):
                self.assertTrue(
                    full_path.exists() and full_path.is_dir(),
                    f"Directory not found: {dir_path}"
                )

    def test_python_version(self):
        """Verify that the Python version is 3.7 or higher."""
        self.assertGreaterEqual(
            sys.version_info,
            (3, 7),
            "Python 3.7 or higher is required"
        )

    def test_required_packages(self):
        """Verify that required packages are installed."""
        required_packages = [
            'sc2',
            'numpy',
            'loguru'
        ]
        
        for package in required_packages:
            with self.subTest(package=package):
                try:
                    importlib.import_module(package)
                except ImportError:
                    self.fail(f"Required package not found: {package}")

if __name__ == '__main__':
    unittest.main()
