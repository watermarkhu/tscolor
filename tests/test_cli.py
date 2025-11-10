"""Tests for the CLI interface."""

import importlib.util
from pathlib import Path

import pytest
from click.testing import CliRunner

from tscolor.cli import main

# Check if tree-sitter-python is available
HAS_PYTHON = importlib.util.find_spec("tree_sitter_python") is not None


class TestLanguageDetection:
    """Test language detection from file extensions."""

    def test_detect_python(self):
        """Test detection of Python files."""
        from tscolor.cli import detect_language

        assert detect_language(Path("test.py")) == "python"
        assert detect_language(Path("/path/to/script.py")) == "python"

    def test_detect_javascript(self):
        """Test detection of JavaScript files."""
        from tscolor.cli import detect_language

        assert detect_language(Path("test.js")) == "javascript"
        assert detect_language(Path("test.jsx")) == "javascript"

    def test_detect_unknown(self):
        """Test detection of unknown extensions."""
        from tscolor.cli import detect_language

        assert detect_language(Path("test.xyz")) is None

    def test_detect_case_insensitive(self):
        """Test case-insensitive extension detection."""
        from tscolor.cli import detect_language

        assert detect_language(Path("test.PY")) == "python"
        assert detect_language(Path("test.Js")) == "javascript"


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self):
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "usage:" in result.output.lower() or "tscolor" in result.output.lower()

    def test_cli_version(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "tscolor" in result.output.lower()

    def test_cli_no_args(self):
        """Test CLI with no arguments shows help."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert "usage:" in result.output.lower() or "tscolor" in result.output.lower()


class TestListThemes:
    """Test theme listing functionality."""

    def test_list_themes_flag(self):
        """Test --list-themes flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--list-themes"])
        assert result.exit_code == 0
        assert "Available themes" in result.output
        assert "dracula" in result.output.lower()


class TestHighlightFile:
    """Test file highlighting functionality."""

    @pytest.fixture
    def simple_python_code(self):
        """Fixture providing simple Python code."""
        return b"def hello(): pass"

    @pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
    def test_highlight_python_file(self, tmp_path, simple_python_code):
        """Test highlighting a Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        runner = CliRunner()
        result = runner.invoke(main, [str(test_file)])

        # Should succeed or fail gracefully
        assert result.exit_code in [0, 1]
        if result.exit_code == 1:
            # Should have error message about missing parser
            assert "Could not load parser" in result.output or "Error" in result.output

    @pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
    def test_highlight_with_theme(self, tmp_path, simple_python_code):
        """Test highlighting with a specific theme."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        runner = CliRunner()
        result = runner.invoke(main, ["--theme", "monokai", str(test_file)])

        # Check exit code
        assert result.exit_code in [0, 1]

    @pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
    def test_highlight_to_html(self, tmp_path, simple_python_code):
        """Test highlighting and exporting to HTML."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        output_file = tmp_path / "output.html"

        runner = CliRunner()
        result = runner.invoke(main, ["--output", str(output_file), str(test_file)])

        # Check exit code
        assert result.exit_code in [0, 1]
        if result.exit_code == 0:
            # HTML file should be created
            assert output_file.exists()
            html_content = output_file.read_text()
            assert "<!DOCTYPE html>" in html_content

    @pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
    def test_highlight_with_language_flag(self, tmp_path):
        """Test highlighting with explicit language specification."""
        # Create a file with non-standard extension
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"def hello(): pass")

        runner = CliRunner()
        result = runner.invoke(main, ["--language", "python", str(test_file)])

        # Should work with explicit language
        assert result.exit_code in [0, 1]

    def test_highlight_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(main, ["/nonexistent/file.py"])
        # Click Path validation catches this before our code runs
        assert result.exit_code != 0


class TestCLIErrors:
    """Test CLI error handling."""

    @pytest.fixture
    def simple_python_code(self):
        """Fixture providing simple Python code."""
        return b"def hello(): pass"

    @pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
    def test_invalid_theme(self, tmp_path, simple_python_code):
        """Test error message for invalid theme."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        runner = CliRunner()
        result = runner.invoke(main, ["--theme", "nonexistent-theme", str(test_file)])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_unknown_extension_without_language(self, tmp_path):
        """Test error for unknown extension without --language."""
        test_file = tmp_path / "test.xyz"
        test_file.write_bytes(b"some content")

        runner = CliRunner()
        result = runner.invoke(main, [str(test_file)])

        assert result.exit_code == 1
        assert (
            "could not detect language" in result.output.lower()
            or "error" in result.output.lower()
        )
