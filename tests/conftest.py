"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
from typing import Any

# Check for optional dependencies
try:
    import tree_sitter_python as ts_python

    HAS_PYTHON = True
except ImportError:
    HAS_PYTHON = False
    ts_python: Any = None

try:
    import tree_sitter_javascript as ts_javascript

    HAS_JAVASCRIPT = True
except ImportError:
    HAS_JAVASCRIPT = False
    ts_javascript: Any = None

# Check if the Rust binary is available
RUST_BINARY = Path(__file__).parent.parent / "target" / "release" / "ts-highlight"
HAS_RUST_BINARY = RUST_BINARY.exists()


# Pytest marks for skipping tests based on availability
pytestmark = pytest.mark.skipif


@pytest.fixture
def rust_binary_path():
    """Path to the Rust tree-sitter-highlight binary."""
    return RUST_BINARY


@pytest.fixture
def tree_sitter_python():
    """tree-sitter-python module if available."""
    if not HAS_PYTHON:
        pytest.skip("tree-sitter-python not installed")
    return ts_python


@pytest.fixture
def tree_sitter_javascript():
    """tree-sitter-javascript module if available."""
    if not HAS_JAVASCRIPT:
        pytest.skip("tree-sitter-javascript not installed")
    return ts_javascript


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
