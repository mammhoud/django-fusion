"""Pytest configuration for pos-full tests.

Registers the fixtures module so pytest can discover the `rust_db`
fixture without requiring explicit imports in test files.
"""

pytest_plugins = ["tests.fixtures"]
