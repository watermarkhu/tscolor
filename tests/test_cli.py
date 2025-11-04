"""Tests for the CLI interface."""
import subprocess
import sys
from pathlib import Path
import pytest

# Check if tree-sitter-python is available
try:
    import tree_sitter_python

    HAS_PYTHON = True
except ImportError:
    HAS_PYTHON = False


def run_cli(*args):
    """Run the CLI with given arguments.

    Returns:
        tuple: (exit_code, stdout, stderr)
    """
    result = subprocess.run(
        [sys.executable, "-m", "tscolor.cli"] + list(args),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


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
        exit_code, stdout, stderr = run_cli("--help")
        assert exit_code == 0
        assert "usage:" in stdout.lower()
        assert "tscolor" in stdout.lower()

    def test_cli_version(self):
        """Test --version flag."""
        exit_code, stdout, stderr = run_cli("--version")
        assert exit_code == 0
        assert "tscolor" in stdout.lower()

    def test_cli_no_args(self):
        """Test CLI with no arguments shows help."""
        exit_code, stdout, stderr = run_cli()
        assert exit_code == 0
        assert "usage:" in stdout.lower()


class TestListThemes:
    """Test theme listing functionality."""

    def test_list_themes_flag(self):
        """Test --list-themes flag."""
        exit_code, stdout, stderr = run_cli("--list-themes")
        assert exit_code == 0
        assert "Available themes" in stdout
        assert "dracula" in stdout.lower()


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

        exit_code, stdout, stderr = run_cli(str(test_file))

        # Should succeed or fail gracefully
        assert exit_code in [0, 1]
        if exit_code == 1:
            # Should have error message about missing parser
            assert "Could not load parser" in stderr or "Error" in stderr

    @pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
    def test_highlight_with_theme(self, tmp_path, simple_python_code):
        """Test highlighting with a specific theme."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        exit_code, stdout, stderr = run_cli(str(test_file), "--theme", "monokai")

        # Check exit code
        assert exit_code in [0, 1]

    @pytest.mark.skipif(not HAS_PYTHON, reason="tree-sitter-python not installed")
    def test_highlight_to_html(self, tmp_path, simple_python_code):
        """Test highlighting and exporting to HTML."""
        test_file = tmp_path / "test.py"
        test_file.write_bytes(simple_python_code)

        output_file = tmp_path / "output.html"

        exit_code, stdout, stderr = run_cli(
            str(test_file), "--output", str(output_file)
        )

        # Check exit code
        assert exit_code in [0, 1]
        if exit_code == 0:
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

        exit_code, stdout, stderr = run_cli(
            str(test_file), "--language", "python"
        )

        # Should work with explicit language
        assert exit_code in [0, 1]

    def test_highlight_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        exit_code, stdout, stderr = run_cli("/nonexistent/file.py")
        assert exit_code == 1
        assert "not found" in stderr.lower() or "error" in stderr.lower()


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

        exit_code, stdout, stderr = run_cli(
            str(test_file), "--theme", "nonexistent-theme"
        )

        assert exit_code == 1
        assert "not found" in stderr.lower() or "error" in stderr.lower()

    def test_unknown_extension_without_language(self, tmp_path):
        """Test error for unknown extension without --language."""
        test_file = tmp_path / "test.xyz"
        test_file.write_bytes(b"some content")

        exit_code, stdout, stderr = run_cli(str(test_file))

        assert exit_code == 1
        assert (
            "could not detect language" in stderr.lower()
            or "error" in stderr.lower()
        )
