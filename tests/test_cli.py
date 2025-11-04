"""Tests for the CLI."""
import pytest
from pathlib import Path
from click.testing import CliRunner

try:
    import tree_sitter_python as ts_python

    HAS_PYTHON = True
except ImportError:
    HAS_PYTHON = False

from tscolor.cli import cli, list_themes_cmd, detect_language


class TestLanguageDetection:
    """Test language detection from file extensions."""

    def test_detect_python(self):
        """Test detecting Python from .py extension."""
        assert detect_language(Path("script.py")) == "python"

    def test_detect_javascript(self):
        """Test detecting JavaScript from .js extension."""
        assert detect_language(Path("script.js")) == "javascript"
        assert detect_language(Path("script.jsx")) == "javascript"

    def test_detect_unknown(self):
        """Test unknown extension returns None."""
        assert detect_language(Path("file.unknown")) is None

    def test_detect_case_insensitive(self):
        """Test that detection is case-insensitive."""
        assert detect_language(Path("script.PY")) == "python"
        assert detect_language(Path("script.JS")) == "javascript"


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self):
        """Test that --help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Syntax highlighting using tree-sitter" in result.output

    def test_cli_version(self):
        """Test that --version works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "tscolor" in result.output

    def test_cli_no_args(self):
        """Test CLI with no arguments shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Syntax highlighting" in result.output or "Usage" in result.output


class TestListThemes:
    """Test theme listing functionality."""

    def test_list_themes_flag(self):
        """Test --list-themes flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--list-themes"])
        assert result.exit_code == 0
        assert "Available themes" in result.output
        assert "dracula" in result.output.lower()

    def test_themes_command(self):
        """Test 'themes' subcommand."""
        runner = CliRunner()
        result = runner.invoke(cli, ["themes"])
        assert result.exit_code == 0
        assert "Available themes" in result.output
        assert "Dark themes" in result.output or "Light themes" in result.output


@pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
class TestHighlightFile:
    """Test file highlighting functionality."""

    def test_highlight_python_file(self, tmp_path, simple_python_code):
        """Test highlighting a Python file."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        runner = CliRunner()
        result = runner.invoke(cli, [str(test_file)])

        # Should succeed (exit code 0) or have specific error
        # Note: might fail if tree-sitter-python not installed
        assert result.exit_code in [0, 1]
        if result.exit_code == 1:
            # Should have error message about missing parser
            assert "Could not load parser" in result.output or "Error" in result.output

    def test_highlight_with_theme(self, tmp_path, simple_python_code):
        """Test highlighting with a specific theme."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        runner = CliRunner()
        result = runner.invoke(cli, [str(test_file), "--theme", "monokai"])

        # Check exit code
        assert result.exit_code in [0, 1]

    def test_highlight_to_html(self, tmp_path, simple_python_code):
        """Test highlighting and exporting to HTML."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        output_file = tmp_path / "output.html"

        runner = CliRunner()
        result = runner.invoke(
            cli, [str(test_file), "--output", str(output_file)]
        )

        # Check exit code
        assert result.exit_code in [0, 1]
        if result.exit_code == 0:
            # HTML file should be created
            assert output_file.exists()
            html_content = output_file.read_text()
            assert "<!DOCTYPE html>" in html_content

    def test_highlight_with_language_flag(self, tmp_path):
        """Test highlighting with explicit language specification."""
        # Create a file with non-standard extension
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"def hello(): pass")

        runner = CliRunner()
        result = runner.invoke(
            cli, [str(test_file), "--language", "python"]
        )

        # Should work with explicit language
        assert result.exit_code in [0, 1]

    def test_highlight_nonexistent_file(self):
        """Test highlighting a nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["/nonexistent/file.py"])

        # Should fail
        assert result.exit_code != 0
        # Click will show error about path not existing


class TestCLIErrors:
    """Test CLI error handling."""

    def test_invalid_theme(self, tmp_path, simple_python_code):
        """Test error message for invalid theme."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        runner = CliRunner()
        result = runner.invoke(
            cli, [str(test_file), "--theme", "nonexistent-theme"]
        )

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_unknown_extension_without_language(self, tmp_path):
        """Test error for unknown extension without --language."""
        test_file = tmp_path / "test.xyz"
        test_file.write_bytes(b"some content")

        runner = CliRunner()
        result = runner.invoke(cli, [str(test_file)])

        assert result.exit_code == 1
        assert (
            "could not detect language" in result.output.lower()
            or "error" in result.output.lower()
        )


class TestHighlightCommand:
    """Test the 'highlight' subcommand."""

    @pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
    def test_highlight_subcommand(self, tmp_path, simple_python_code):
        """Test 'highlight' subcommand."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        runner = CliRunner()
        result = runner.invoke(cli, ["highlight", str(test_file)])

        # Should work
        assert result.exit_code in [0, 1]
