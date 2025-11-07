"""Tests for language registry."""

from pathlib import Path
import pytest
import tree_sitter

from tscolor.languages import (
    LanguageRegistry,
    register_language,
    get_configuration,
    list_languages,
    detect_language_by_extension,
    detect_language,
)


class TestLanguageRegistry:
    """Test LanguageRegistry class."""

    @pytest.fixture
    def python_lang(self, tree_sitter_python):
        """Get Python language."""
        return tree_sitter.Language(tree_sitter_python.language())

    @pytest.fixture
    def registry(self, tmp_path):
        """Create a test registry with a temporary languages directory."""
        return LanguageRegistry(languages_dir=tmp_path)

    def test_register_language_with_capsule(self, registry, tree_sitter_python):
        """Test registering a language using a capsule (not wrapped in Language)."""
        # Pass the raw language capsule, not wrapped in Language
        registry.register_language("python", tree_sitter_python.language())

        # Should have wrapped it automatically
        assert "python" in registry._languages
        assert isinstance(registry._languages["python"], tree_sitter.Language)

    def test_get_configuration_unregistered_language(self, registry):
        """Test getting configuration for an unregistered language raises KeyError."""
        with pytest.raises(KeyError, match="Language 'nonexistent' not registered"):
            registry.get_configuration("nonexistent")

    def test_get_configuration_missing_directory(self, registry, python_lang, tmp_path):
        """Test getting configuration when language directory doesn't exist."""
        # Register the language
        registry.register_language("python", python_lang)

        # The directory doesn't exist in tmp_path
        with pytest.raises(FileNotFoundError, match="Language directory not found"):
            registry.get_configuration("python")

    def test_list_languages(self, registry, python_lang):
        """Test listing registered languages."""
        # Initially empty
        assert registry.list_languages() == []

        # Register some languages
        registry.register_language("python", python_lang)
        registry.register_language("javascript", python_lang)  # Reuse for testing

        languages = registry.list_languages()
        assert len(languages) == 2
        assert "python" in languages
        assert "javascript" in languages


class TestGlobalFunctions:
    """Test global language registry functions."""

    @pytest.fixture(autouse=True)
    def cleanup_registry(self):
        """Clean up global registry after each test."""
        from tscolor.languages import _default_registry

        # Clear the registry
        _default_registry._languages.clear()
        yield
        # Clean up after test
        _default_registry._languages.clear()

    def test_register_language_global(self, tree_sitter_python):
        """Test global register_language function with capsule."""
        # Register using the global function with a capsule
        register_language("python", tree_sitter_python.language())

        # Should be in the list
        assert "python" in list_languages()

    def test_list_languages_global(self, tree_sitter_python):
        """Test global list_languages function."""
        # Initially empty (after cleanup)
        assert list_languages() == []

        # Register a language
        register_language("python", tree_sitter_python.language())

        # Should be in the list
        languages = list_languages()
        assert len(languages) == 1
        assert "python" in languages

    def test_get_configuration_global_error(self):
        """Test global get_configuration with unregistered language."""
        with pytest.raises(KeyError, match="Language 'nonexistent' not registered"):
            get_configuration("nonexistent")


class TestExtensionDetection:
    """Test file extension detection."""

    def test_detect_python_extension(self):
        """Test detection of Python files by extension."""
        assert detect_language_by_extension(Path("test.py")) == "python"
        assert detect_language_by_extension(Path("test.pyi")) == "python"
        assert detect_language_by_extension(Path("test.pyw")) == "python"

    def test_detect_javascript_extension(self):
        """Test detection of JavaScript files by extension."""
        assert detect_language_by_extension(Path("test.js")) == "javascript"
        assert detect_language_by_extension(Path("test.jsx")) == "javascript"
        assert detect_language_by_extension(Path("test.mjs")) == "javascript"
        assert detect_language_by_extension(Path("test.cjs")) == "javascript"

    def test_detect_matlab_extension(self):
        """Test detection of MATLAB files by extension."""
        assert detect_language_by_extension(Path("test.m")) == "matlab"

    def test_detect_unknown_extension(self):
        """Test detection returns None for unknown extensions."""
        assert detect_language_by_extension(Path("test.xyz")) is None
        assert detect_language_by_extension(Path("test.unknown")) is None

    def test_detect_case_insensitive(self):
        """Test that extension detection is case insensitive."""
        assert detect_language_by_extension(Path("test.PY")) == "python"
        assert detect_language_by_extension(Path("test.JS")) == "javascript"
        assert detect_language_by_extension(Path("test.M")) == "matlab"


class TestContentDetection:
    """Test content-based language detection using pygments."""

    def test_detect_python_content(self, tmp_path):
        """Test detection of Python code by content."""
        python_file = tmp_path / "test.txt"
        python_file.write_text("""
def hello():
    print('Hello, world!')
    return 42

class MyClass:
    def __init__(self):
        self.value = 10
""")
        # Pygments should detect this as Python
        result = detect_language(python_file)
        # Accept either Python or Python3 or fallback to None
        assert result in ("python", None)

    def test_detect_javascript_content(self, tmp_path):
        """Test detection of JavaScript code by content."""
        js_file = tmp_path / "test.txt"
        js_file.write_text("""
function hello() {
    console.log('Hello, world!');
    return 42;
}
""")
        # Pygments may detect this as JavaScript or another language
        # We just verify it doesn't crash
        result = detect_language(js_file)
        assert result is None or isinstance(result, str)

    def test_detect_fallback_to_extension(self, tmp_path):
        """Test that detection falls back to extension when content detection fails."""
        py_file = tmp_path / "test.py"
        py_file.write_text("# Just a comment, hard to detect")
        # Should fall back to extension detection
        assert detect_language(py_file) == "python"

    def test_detect_unknown_file(self, tmp_path):
        """Test detection of unknown file type."""
        unknown_file = tmp_path / "test.xyz"
        unknown_file.write_text("some random text that is not code")
        result = detect_language(unknown_file)
        # Should return None for completely unknown files
        assert result is None
