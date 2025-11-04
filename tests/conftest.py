"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return b"""
def factorial(n):
    '''Calculate factorial.'''
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""


@pytest.fixture
def sample_javascript_code():
    """Sample JavaScript code for testing."""
    return b"""
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
"""


@pytest.fixture
def simple_python_code():
    """Very simple Python code for testing."""
    return b"def hello(): pass"


@pytest.fixture
def themes_dir():
    """Get the themes directory."""
    return Path(__file__).parent.parent / "themes"
