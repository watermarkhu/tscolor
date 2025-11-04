"""Tests for output formatters."""

import pytest

try:
    import tree_sitter_python as ts_python

    HAS_PYTHON = True
except ImportError:
    HAS_PYTHON = False

from tscolor import Highlighter, get_theme
from tscolor.languages import register_language, get_configuration
from tscolor.formatters import AnsiFormatter, HtmlFormatter


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestAnsiFormatter:
    """Test ANSI color formatter."""

    def test_formatter_initialization(self):
        """Test that ANSI formatter can be initialized."""
        theme = get_theme("dracula")
        formatter = AnsiFormatter(theme)
        assert formatter is not None
        assert formatter.theme == theme

    def test_format_simple_code(self, simple_python_code):
        """Test formatting simple code with ANSI colors."""
        register_language("python", ts_python.language())
        theme = get_theme("dracula")
        highlighter = Highlighter()
        config = get_configuration("python")

        events = highlighter.highlight(config, simple_python_code)
        formatter = AnsiFormatter(theme)
        result = formatter.format(simple_python_code, events, config)

        # Should return a string
        assert isinstance(result, str)
        # Should contain ANSI escape codes
        assert "\033[" in result
        # Should contain reset code
        assert "\033[0m" in result

    def test_format_contains_source_text(self, simple_python_code):
        """Test that formatted output contains source text."""
        register_language("python", ts_python.language())
        theme = get_theme("dracula")
        highlighter = Highlighter()
        config = get_configuration("python")

        events = highlighter.highlight(config, simple_python_code)
        formatter = AnsiFormatter(theme)
        result = formatter.format(simple_python_code, events, config)

        # Should contain the function definition
        assert "def" in result or "hello" in result

    def test_format_with_background(self, simple_python_code):
        """Test formatting with background color."""
        register_language("python", ts_python.language())
        theme = get_theme("dracula")
        highlighter = Highlighter()
        config = get_configuration("python")

        events = highlighter.highlight(config, simple_python_code)
        formatter = AnsiFormatter(theme)
        result = formatter.format_with_background(simple_python_code, events, config)

        # Should contain background color code
        assert "\033[48;2;" in result


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestHtmlFormatter:
    """Test HTML formatter."""

    def test_formatter_initialization(self):
        """Test that HTML formatter can be initialized."""
        theme = get_theme("dracula")
        formatter = HtmlFormatter(theme)
        assert formatter is not None
        assert formatter.theme == theme

    def test_format_simple_code(self, simple_python_code):
        """Test formatting simple code as HTML."""
        register_language("python", ts_python.language())
        theme = get_theme("dracula")
        highlighter = Highlighter()
        config = get_configuration("python")

        events = highlighter.highlight(config, simple_python_code)
        formatter = HtmlFormatter(theme)
        result = formatter.format(
            simple_python_code, events, config, inline_styles=True
        )

        # Should return a string
        assert isinstance(result, str)
        # Should contain HTML span tags
        assert "<span" in result
        # Should contain style attributes
        assert "style=" in result or "color:" in result

    def test_format_with_css_classes(self, simple_python_code):
        """Test formatting with CSS classes instead of inline styles."""
        register_language("python", ts_python.language())
        theme = get_theme("dracula")
        highlighter = Highlighter()
        config = get_configuration("python")

        events = highlighter.highlight(config, simple_python_code)
        formatter = HtmlFormatter(theme, class_prefix="hl-")
        result = formatter.format(
            simple_python_code, events, config, inline_styles=False
        )

        # Should contain class attributes
        assert 'class="hl-' in result

    def test_format_complete_document(self, simple_python_code):
        """Test generating complete HTML document."""
        register_language("python", ts_python.language())
        theme = get_theme("dracula")
        highlighter = Highlighter()
        config = get_configuration("python")

        events = highlighter.highlight(config, simple_python_code)
        formatter = HtmlFormatter(theme)
        result = formatter.format_complete(simple_python_code, events, config)

        # Should be a complete HTML document
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "<style>" in result

    def test_generate_css(self):
        """Test CSS stylesheet generation."""
        register_language("python", ts_python.language())
        theme = get_theme("dracula")
        config = get_configuration("python")
        formatter = HtmlFormatter(theme)

        css = formatter.generate_css(config)

        # Should return a string
        assert isinstance(css, str)
        # Should contain CSS rules
        assert "{" in css and "}" in css
        # Should contain color properties
        assert "color:" in css

    def test_html_escape(self):
        """Test that HTML special characters are escaped."""
        register_language("python", ts_python.language())
        theme = get_theme("dracula")
        highlighter = Highlighter()
        config = get_configuration("python")

        # Code with HTML special characters
        code = b'x = "<html> & </html>"'
        events = highlighter.highlight(config, code)
        formatter = HtmlFormatter(theme)
        result = formatter.format(code, events, config)

        # Should escape HTML entities
        assert "&lt;" in result or "&gt;" in result or "&amp;" in result


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestFormatterWithDifferentThemes:
    """Test formatters with different themes."""

    def test_ansi_with_light_theme(self, simple_python_code):
        """Test ANSI formatter with light theme."""
        register_language("python", ts_python.language())
        theme = get_theme("github-light")
        highlighter = Highlighter()
        config = get_configuration("python")

        events = highlighter.highlight(config, simple_python_code)
        formatter = AnsiFormatter(theme)
        result = formatter.format(simple_python_code, events, config)

        assert isinstance(result, str)
        assert "\033[" in result

    def test_html_with_dark_theme(self, simple_python_code):
        """Test HTML formatter with dark theme."""
        register_language("python", ts_python.language())
        theme = get_theme("monokai")
        highlighter = Highlighter()
        config = get_configuration("python")

        events = highlighter.highlight(config, simple_python_code)
        formatter = HtmlFormatter(theme)
        result = formatter.format_complete(simple_python_code, events, config)

        # Should have dark background
        assert "#272822" in result  # Monokai background
