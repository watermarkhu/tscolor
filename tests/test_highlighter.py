"""Tests for the syntax highlighter."""

import pytest
import tree_sitter

from tscolor import Highlighter
from tscolor import SourceEvent, HighlightStartEvent, HighlightEndEvent
from tscolor.languages import register_language, get_configuration
from tscolor.configuration import HighlightConfiguration

# Import from conftest
from tests.conftest import HAS_PYTHON, HAS_JAVASCRIPT, ts_python, ts_javascript


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

        # Consume the iterator to trigger cancellation checks
        list(highlighter.highlight(config, sample_python_code, should_cancel))

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


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestNodeHighlighting:
    """Test highlighting individual tree-sitter nodes."""

    def test_highlight_node(self):
        """Test highlighting a specific node."""
        from tscolor.languages import register_language, get_configuration

        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        # Parse code to get a tree
        source = b"def hello():\n    pass"
        parser = tree_sitter.Parser(tree_sitter.Language(ts_python.language()))
        tree = parser.parse(source)

        # Get the function definition node
        func_node = tree.root_node.children[0]

        # Highlight just that node
        events = list(highlighter.highlight_node(config, func_node, tree))

        # Should have some events
        assert len(events) > 0

        # Should have source and highlight events
        event_types = {type(e).__name__ for e in events}
        assert "SourceEvent" in event_types or "HighlightStartEvent" in event_types

    def test_highlight_node_with_range(self):
        """Test that highlight_node respects node boundaries."""
        from tscolor.languages import register_language, get_configuration

        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        # Parse code with multiple statements
        source = b"x = 1\ny = 2\nz = 3"
        parser = tree_sitter.Parser(tree_sitter.Language(ts_python.language()))
        tree = parser.parse(source)

        # Get the second statement node (y = 2)
        second_stmt = tree.root_node.children[1]

        # Highlight just that node
        events = list(highlighter.highlight_node(config, second_stmt, tree))

        # Collect all byte positions from events
        positions = set()
        for event in events:
            if hasattr(event, "start"):
                positions.add(event.start)
                positions.add(event.end)

        # All positions should be within the node's range
        for pos in positions:
            assert second_stmt.start_byte <= pos <= second_stmt.end_byte


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestLanguageInjection:
    """Test language injection support."""

    def test_register_injection_language(self):
        """Test registering an injection language."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()

        # Register JavaScript as an injection language
        if HAS_JAVASCRIPT:
            js_config = HighlightConfiguration(
                language=tree_sitter.Language(ts_javascript.language()),
                highlights_query="(identifier) @variable",
            )
            highlighter.register_injection_language("javascript", js_config)

            # Verify it's registered
            assert "javascript" in highlighter._injection_configs
            assert highlighter._injection_configs["javascript"] == js_config

    def test_highlight_with_injections_query(self):
        """Test highlighting with an injections query."""
        register_language("python", ts_python.language())
        lang = tree_sitter.Language(ts_python.language())

        # Create a simple injections query that looks for strings
        highlights_query = "(identifier) @variable"
        injections_query = """
(string) @injection.content
"""

        config = HighlightConfiguration(
            language=lang,
            highlights_query=highlights_query,
            injections_query=injections_query,
        )

        highlighter = Highlighter()
        source = b'x = "hello world"'

        # This won't actually inject anything since we didn't register
        # an injection language, but it should execute without error
        events = list(highlighter.highlight(config, source))
        assert len(events) > 0


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestLocalScopeTracking:
    """Test local scope and variable tracking."""

    def test_highlight_with_local_scope_query(self):
        """Test highlighting with local scope tracking."""
        lang = tree_sitter.Language(ts_python.language())

        # Create queries with local scope tracking
        highlights_query = "(identifier) @variable"
        locals_query = """
(function_definition) @local.scope
(parameters (identifier) @local.definition)
"""

        config = HighlightConfiguration(
            language=lang,
            highlights_query=highlights_query,
            locals_query=locals_query,
        )

        highlighter = Highlighter()
        source = b"def foo(x):\n    return x"

        # Should process local scopes
        events = list(highlighter.highlight(config, source))
        assert len(events) > 0

    def test_highlight_with_local_reference(self):
        """Test highlighting with local reference resolution."""
        lang = tree_sitter.Language(ts_python.language())

        # Create queries with local reference tracking
        highlights_query = "(identifier) @variable"
        locals_query = """
(function_definition) @local.scope
(parameters (identifier) @local.definition)
(identifier) @local.reference
"""

        config = HighlightConfiguration(
            language=lang,
            highlights_query=highlights_query,
            locals_query=locals_query,
        )

        highlighter = Highlighter()
        source = b"def foo(x):\n    y = x\n    return y"

        # Should resolve local references
        events = list(highlighter.highlight(config, source))
        assert len(events) > 0


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_sorted_events(self):
        """Test highlighting when there are no highlight events."""
        register_language("python", ts_python.language())
        lang = tree_sitter.Language(ts_python.language())

        # Create a config with a query that will never match (looking for import in code without imports)
        highlights_query = (
            '((import_statement) @keyword (#eq? @keyword "import_that_does_not_exist"))'
        )

        config = HighlightConfiguration(
            language=lang,
            highlights_query=highlights_query,
        )

        highlighter = Highlighter()
        source = b"def foo(): pass"

        # Should handle gracefully and just emit source events
        events = list(highlighter.highlight(config, source))

        # Should have at least one source event for the whole source
        source_events = [e for e in events if isinstance(e, SourceEvent)]
        assert len(source_events) >= 1

    def test_highlight_with_byte_range(self):
        """Test highlighting constrained to a byte range."""
        register_language("python", ts_python.language())
        highlighter = Highlighter()
        config = get_configuration("python")

        source = b"x = 1\ny = 2\nz = 3"
        parser = tree_sitter.Parser(tree_sitter.Language(ts_python.language()))
        tree = parser.parse(source)

        # Get the second line node
        second_stmt = tree.root_node.children[1]

        # Use highlight_node which uses byte_range internally
        events = list(highlighter.highlight_node(config, second_stmt, tree))

        # Should have events
        assert len(events) > 0

        # All events should be within the node's range
        for event in events:
            if isinstance(event, SourceEvent):
                assert event.start >= second_stmt.start_byte
                assert event.end <= second_stmt.end_byte
