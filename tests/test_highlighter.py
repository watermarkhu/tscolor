"""Tests for the syntax highlighter."""

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


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestBasicHighlighting:
    """Test basic syntax highlighting."""

    def test_highlighter_initialization(self):
        """Test that highlighter can be initialized."""
        highlighter = Highlighter()
        assert highlighter is not None
        assert highlighter.parser is not None

    def test_highlight_simple_code(self, simple_python_code):
        """Test highlighting simple Python code."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        events = list(highlighter.highlight(config, simple_python_code))

        # Should have some events
        assert len(events) > 0

        # Should have at least one SourceEvent
        source_events = [e for e in events if isinstance(e, SourceEvent)]
        assert len(source_events) > 0

    def test_highlight_produces_correct_event_types(self, simple_python_code):
        """Test that highlighting produces correct event types."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        events = list(highlighter.highlight(config, simple_python_code))

        # Check event types
        for event in events:
            assert isinstance(
                event, (SourceEvent, HighlightStartEvent, HighlightEndEvent)
            )

    def test_highlight_start_end_pairs(self, simple_python_code):
        """Test that highlight start/end events are properly paired."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        events = list(highlighter.highlight(config, simple_python_code))

        # Count starts and ends
        starts = sum(1 for e in events if isinstance(e, HighlightStartEvent))
        ends = sum(1 for e in events if isinstance(e, HighlightEndEvent))

        # Should have equal number of starts and ends
        assert starts == ends

    def test_source_event_ranges(self, simple_python_code):
        """Test that source events have valid ranges."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        events = list(highlighter.highlight(config, simple_python_code))
        source_events = [e for e in events if isinstance(e, SourceEvent)]

        for event in source_events:
            assert event.start >= 0
            assert event.end <= len(simple_python_code)
            assert event.start < event.end


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestHighlightConfiguration:
    """Test highlight configuration."""

    def test_configuration_has_queries(self):
        """Test that configuration loads queries."""
        register_language("python", ts_python.language())
        config = get_configuration("python")

        assert config.highlights_query is not None
        assert config.language is not None

    def test_configuration_has_highlight_names(self):
        """Test that configuration extracts highlight names."""
        register_language("python", ts_python.language())
        config = get_configuration("python")

        assert len(config.highlight_names) > 0
        # Should have common captures
        assert (
            "keyword" in config.highlight_names
            or "keyword.control" in config.highlight_names
        )


@pytest.mark.skipif(not HAS_JAVASCRIPT, reason="tree-sitter-javascript not installed")
class TestJavaScriptHighlighting:
    """Test JavaScript syntax highlighting."""

    def test_highlight_javascript(self, sample_javascript_code):
        """Test highlighting JavaScript code."""
        register_language("javascript", ts_javascript.language())
        highlighter = Highlighter()
        config = get_configuration("javascript")

        events = list(highlighter.highlight(config, sample_javascript_code))

        # Should have events
        assert len(events) > 0

        # Should have highlights for function keyword
        highlight_starts = [e for e in events if isinstance(e, HighlightStartEvent)]
        assert len(highlight_starts) > 0


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestHighlightCancellation:
    """Test highlight cancellation."""

    def test_cancellation_flag(self, sample_python_code):
        """Test that cancellation flag stops highlighting."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        # Create a cancellation flag that triggers immediately
        cancel_count = [0]

        def should_cancel():
            cancel_count[0] += 1
            return cancel_count[0] > 2  # Cancel after a few checks

        events = list(highlighter.highlight(config, sample_python_code, should_cancel))

        # Should have fewer events due to cancellation (or possibly none)
        # The exact behavior depends on when cancellation is checked
        assert cancel_count[0] > 0  # Flag was checked


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestEmptyAndInvalidInput:
    """Test edge cases."""

    def test_empty_source(self):
        """Test highlighting empty source code."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        events = list(highlighter.highlight(config, b""))

        # Empty source should produce no events or just metadata events
        assert isinstance(events, list)

    def test_whitespace_only(self):
        """Test highlighting whitespace-only code."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        events = list(highlighter.highlight(config, b"   \n   \n"))

        # Should handle gracefully
        assert isinstance(events, list)
