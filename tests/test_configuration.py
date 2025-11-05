"""Tests for HighlightConfiguration."""

import pytest
import tree_sitter

from tscolor.configuration import HighlightConfiguration, DEFAULT_HIGHLIGHT_NAMES


class TestHighlightConfigurationWithInjections:
    """Test configuration with injections and locals queries."""

    @pytest.fixture
    def python_lang(self, tree_sitter_python):
        """Get Python language."""
        return tree_sitter.Language(tree_sitter_python.language())

    def test_configuration_with_injections_query(self, python_lang):
        """Test configuration with injections query."""
        highlights_query = "(identifier) @variable"
        injections_query = "\n(comment) @comment"  # Need newline for pattern counting

        config = HighlightConfiguration(
            language=python_lang,
            highlights_query=highlights_query,
            injections_query=injections_query,
        )

        assert config.injections_query is not None
        assert config.locals_pattern_index > 0

    def test_configuration_with_locals_query(self, python_lang):
        """Test configuration with locals query."""
        highlights_query = "(identifier) @variable"
        locals_query = (
            "\n(function_definition) @local.scope"  # Need newline for pattern counting
        )

        config = HighlightConfiguration(
            language=python_lang,
            highlights_query=highlights_query,
            locals_query=locals_query,
        )

        assert config.locals_query is not None
        assert config.highlights_pattern_index > 0

    def test_configuration_with_all_queries(self, python_lang):
        """Test configuration with injections, locals, and highlights queries."""
        highlights_query = "(identifier) @variable"
        injections_query = "\n(string) @string"  # Need newline for pattern counting
        locals_query = (
            "\n(function_definition) @local.scope"  # Need newline for pattern counting
        )

        config = HighlightConfiguration(
            language=python_lang,
            highlights_query=highlights_query,
            injections_query=injections_query,
            locals_query=locals_query,
        )

        assert config.injections_query is not None
        assert config.locals_query is not None
        assert config.highlights_pattern_index > 0
        assert config.locals_pattern_index > 0

    def test_configuration_with_custom_highlight_names(self, python_lang):
        """Test configuration with explicitly provided highlight names."""
        highlights_query = "(identifier) @variable"
        custom_names = ["variable", "function", "keyword"]

        config = HighlightConfiguration(
            language=python_lang,
            highlights_query=highlights_query,
            highlight_names=custom_names,
        )

        assert config.highlight_names == custom_names
        assert len(config.capture_index_map) == len(custom_names)

    def test_configuration_with_invalid_injections_query_raises(self, python_lang):
        """Test that invalid injections query raises an error immediately."""
        highlights_query = "(identifier) @variable"
        # Create an invalid query - tree-sitter will raise QueryError
        injections_query = "\n(invalid_node_type) @comment"

        # Should raise an error when creating individual queries
        with pytest.raises(tree_sitter.QueryError):
            HighlightConfiguration(
                language=python_lang,
                highlights_query=highlights_query,
                injections_query=injections_query,
            )


class TestDefaultHighlightNames:
    """Test DEFAULT_HIGHLIGHT_NAMES constant."""

    def test_default_highlight_names_count(self):
        """Test that we have exactly 26 standard highlight names."""
        assert len(DEFAULT_HIGHLIGHT_NAMES) == 26

    def test_default_highlight_names_order(self):
        """Test that highlight names are in the expected order."""
        # First few should be in this specific order
        assert DEFAULT_HIGHLIGHT_NAMES[0] == "attribute"
        assert DEFAULT_HIGHLIGHT_NAMES[1] == "comment"
        assert DEFAULT_HIGHLIGHT_NAMES[2] == "constant"
        # Last should be variable.parameter
        assert DEFAULT_HIGHLIGHT_NAMES[-1] == "variable.parameter"


class TestConfigurationFromLanguagePath:
    """Test from_language_path classmethod."""

    @pytest.fixture
    def python_lang(self, tree_sitter_python):
        """Get Python language."""
        return tree_sitter.Language(tree_sitter_python.language())

    def test_from_language_path_missing_highlights(self, python_lang, tmp_path):
        """Test from_language_path when highlights.scm is missing."""
        # Create a language directory without highlights.scm
        lang_dir = tmp_path / "test_lang"
        lang_dir.mkdir()

        with pytest.raises(
            FileNotFoundError, match="Required highlights.scm not found"
        ):
            HighlightConfiguration.from_language_path(
                language=python_lang, language_path=lang_dir
            )

    def test_from_language_path_with_all_files(self, python_lang, tmp_path):
        """Test from_language_path with all query files present."""
        # Create a language directory with all query files
        lang_dir = tmp_path / "test_lang"
        lang_dir.mkdir()

        (lang_dir / "highlights.scm").write_text("(identifier) @variable")
        (lang_dir / "injections.scm").write_text("(comment) @comment")
        (lang_dir / "locals.scm").write_text("(function_definition) @local.scope")

        config = HighlightConfiguration.from_language_path(
            language=python_lang, language_path=lang_dir
        )

        assert config.injections_query is not None
        assert config.locals_query is not None
        assert len(config.highlight_names) == 26  # Should use DEFAULT_HIGHLIGHT_NAMES
