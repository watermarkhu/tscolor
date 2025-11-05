"""Integration tests comparing tscolor output with rust tree-sitter-highlight.

These tests verify that tscolor produces the same highlighting events as the
official rust tree-sitter-highlight library.

To run these tests:
1. Build the Rust helper binary: cargo build --release
2. Run pytest: uv run pytest tests/integration/

The tests will be skipped if the Rust binary is not available.
"""

import subprocess
from pathlib import Path
import pytest

try:
    import tree_sitter_python as ts_python

    HAS_PYTHON = True
except ImportError:
    HAS_PYTHON = False

try:
    import tree_sitter_javascript as ts_javascript

    HAS_JAVASCRIPT = True
except ImportError:
    HAS_JAVASCRIPT = False

from tscolor import Highlighter
from tscolor import SourceEvent, HighlightStartEvent, HighlightEndEvent
from tscolor.languages import register_language, get_configuration


# Check if the Rust binary is available
RUST_BINARY = (
    Path(__file__).parent.parent.parent / "target" / "release" / "ts-highlight"
)
HAS_RUST_BINARY = RUST_BINARY.exists()


def parse_rust_output(output: str) -> list:
    """Parse the output from the Rust tree-sitter-highlight binary.

    The Rust binary outputs events in the format:
    - S:<start>:<end> - Source event
    - HS:<index> - HighlightStart event
    - HE - HighlightEnd event

    Returns:
        List of event tuples matching tscolor's event format
    """
    events = []
    for line in output.strip().split("\n"):
        if not line:
            continue
        parts = line.split(":")
        if parts[0] == "S":
            start, end = int(parts[1]), int(parts[2])
            events.append(("Source", start, end))
        elif parts[0] == "HS":
            index = int(parts[1])
            events.append(("HighlightStart", index))
        elif parts[0] == "HE":
            events.append(("HighlightEnd",))
    return events


def tscolor_events_to_tuples(events: list) -> list:
    """Convert tscolor events to tuples for comparison.

    Args:
        events: List of tscolor event objects

    Returns:
        List of event tuples
    """
    result = []
    for event in events:
        if isinstance(event, SourceEvent):
            result.append(("Source", event.start, event.end))
        elif isinstance(event, HighlightStartEvent):
            result.append(("HighlightStart", event.index))
        elif isinstance(event, HighlightEndEvent):
            result.append(("HighlightEnd",))
    return result


def run_rust_highlighter(language: str, source: bytes) -> list:
    """Run the Rust tree-sitter-highlight binary and return events.

    Args:
        language: Language name (e.g., "python", "javascript")
        source: Source code bytes

    Returns:
        List of event tuples

    Raises:
        subprocess.CalledProcessError: If the binary fails
    """
    result = subprocess.run(
        [str(RUST_BINARY), language],
        input=source,
        capture_output=True,
        check=True,
    )
    return parse_rust_output(result.stdout.decode())


@pytest.mark.skipif(not HAS_RUST_BINARY, reason="Rust binary not built")
@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestPythonAgainstRust:
    """Test Python highlighting against Rust tree-sitter-highlight."""

    @classmethod
    def setup_class(cls):
        """Set up Python language configuration."""
        register_language("python", ts_python.language())
        cls.config = get_configuration("python")
        cls.highlighter = Highlighter()

    def test_simple_function(self):
        """Test highlighting a simple Python function."""
        source = b"def hello():\n    pass"

        # Get tscolor events
        tscolor_events = list(self.highlighter.highlight(self.config, source))
        tscolor_tuples = tscolor_events_to_tuples(tscolor_events)

        # Get Rust events
        rust_tuples = run_rust_highlighter("python", source)

        # Compare
        assert tscolor_tuples == rust_tuples, (
            f"Events don't match:\ntscolor: {tscolor_tuples}\nrust: {rust_tuples}"
        )

    def test_class_definition(self):
        """Test highlighting a Python class."""
        source = b"""class MyClass:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value
"""

        tscolor_events = list(self.highlighter.highlight(self.config, source))
        tscolor_tuples = tscolor_events_to_tuples(tscolor_events)

        rust_tuples = run_rust_highlighter("python", source)

        assert tscolor_tuples == rust_tuples

    def test_string_literals(self):
        """Test highlighting various string literals."""
        source = b'''s1 = "double quotes"
s2 = 'single quotes'
s3 = """triple
double quotes"""
s4 = f"formatted {value}"
'''

        tscolor_events = list(self.highlighter.highlight(self.config, source))
        tscolor_tuples = tscolor_events_to_tuples(tscolor_events)

        rust_tuples = run_rust_highlighter("python", source)

        assert tscolor_tuples == rust_tuples

    def test_comments(self):
        """Test highlighting comments."""
        source = b"""# This is a comment
def func():  # inline comment
    '''This is a docstring'''
    pass
"""

        tscolor_events = list(self.highlighter.highlight(self.config, source))
        tscolor_tuples = tscolor_events_to_tuples(tscolor_events)

        rust_tuples = run_rust_highlighter("python", source)

        assert tscolor_tuples == rust_tuples


@pytest.mark.skipif(not HAS_RUST_BINARY, reason="Rust binary not built")
@pytest.mark.skipif(not HAS_JAVASCRIPT, reason="tree-sitter-javascript not installed")
class TestJavaScriptAgainstRust:
    """Test JavaScript highlighting against Rust tree-sitter-highlight."""

    @classmethod
    def setup_class(cls):
        """Set up JavaScript language configuration."""
        register_language("javascript", ts_javascript.language())
        cls.config = get_configuration("javascript")
        cls.highlighter = Highlighter()

    def test_simple_function(self):
        """Test highlighting a simple JavaScript function."""
        source = b"function hello() {\n  console.log('hello');\n}"

        tscolor_events = list(self.highlighter.highlight(self.config, source))
        tscolor_tuples = tscolor_events_to_tuples(tscolor_events)

        rust_tuples = run_rust_highlighter("javascript", source)

        assert tscolor_tuples == rust_tuples

    def test_arrow_function(self):
        """Test highlighting arrow functions."""
        source = b"const add = (a, b) => a + b;"

        tscolor_events = list(self.highlighter.highlight(self.config, source))
        tscolor_tuples = tscolor_events_to_tuples(tscolor_events)

        rust_tuples = run_rust_highlighter("javascript", source)

        assert tscolor_tuples == rust_tuples

    def test_class_syntax(self):
        """Test highlighting ES6 class syntax."""
        source = b"""class Counter {
  constructor(initial) {
    this.count = initial;
  }

  increment() {
    this.count++;
  }
}
"""

        tscolor_events = list(self.highlighter.highlight(self.config, source))
        tscolor_tuples = tscolor_events_to_tuples(tscolor_events)

        rust_tuples = run_rust_highlighter("javascript", source)

        assert tscolor_tuples == rust_tuples


# Test to verify the Rust binary works
@pytest.mark.skipif(not HAS_RUST_BINARY, reason="Rust binary not built")
def test_rust_binary_availability():
    """Test that the Rust binary can be executed."""
    result = subprocess.run(
        [str(RUST_BINARY), "python"],
        input=b"pass",
        capture_output=True,
    )
    assert result.returncode == 0, f"Rust binary failed: {result.stderr.decode()}"
    output = result.stdout.decode()
    assert len(output) > 0, "Rust binary produced no output"
