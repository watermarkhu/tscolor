"""Configuration for syntax highlighting."""

from pathlib import Path
from typing import List, Optional, Dict
import tree_sitter


# Default highlight names following tree-sitter-highlight's standard order
# This list must match the order used by the Rust tree-sitter-highlight library
DEFAULT_HIGHLIGHT_NAMES = [
    "attribute",
    "comment",
    "constant",
    "constant.builtin",
    "constructor",
    "embedded",
    "error",
    "escape",
    "function",
    "function.builtin",
    "keyword",
    "number",
    "operator",
    "property",
    "punctuation",
    "punctuation.bracket",
    "punctuation.delimiter",
    "punctuation.special",
    "string",
    "string.special",
    "tag",
    "type",
    "type.builtin",
    "variable",
    "variable.builtin",
    "variable.parameter",
]


class HighlightConfiguration:
    """Configuration for syntax highlighting a specific language.

    This class holds the tree-sitter language parser and the queries needed
    for syntax highlighting (highlights, injections, and locals). Following
    the Rust implementation, queries are combined into a single query object
    with pattern indices tracking boundaries.

    Attributes:
        language: The tree-sitter Language instance for parsing
        combined_query: Combined query containing injections + locals + highlights
        locals_pattern_index: Start index of locals patterns
        highlights_pattern_index: Start index of highlights patterns
        highlight_names: List of capture names used in the queries
        non_local_variable_patterns: Set of pattern indices that should not
                                     match local variables
    """

    def __init__(
        self,
        language: tree_sitter.Language,
        highlights_query: str,
        injections_query: Optional[str] = None,
        locals_query: Optional[str] = None,
        highlight_names: Optional[List[str]] = None,
    ):
        """Initialize a highlight configuration.

        Args:
            language: Tree-sitter Language for parsing
            highlights_query: Query string for syntax highlighting
            injections_query: Optional query for language injections
            locals_query: Optional query for local scope tracking
            highlight_names: Optional list of highlight names. If not provided,
                will be extracted from the queries.
        """
        self.language = language
        self.highlights_query_str = highlights_query
        self.injections_query_str = injections_query or ""
        self.locals_query_str = locals_query or ""

        # Build combined query following Rust implementation:
        # injections + locals + highlights
        query_parts = []
        self.locals_pattern_index = 0
        self.highlights_pattern_index = 0

        # Add injections query
        if injections_query:
            query_parts.append(injections_query)
            # Count patterns in injections (approximate by counting parentheses)
            self.locals_pattern_index += injections_query.count("\n(")

        # Add locals query
        if locals_query:
            self.highlights_pattern_index = self.locals_pattern_index
            query_parts.append(locals_query)
            self.highlights_pattern_index += locals_query.count("\n(")

        # Add highlights query
        if not query_parts:
            self.highlights_pattern_index = 0
        query_parts.append(highlights_query)

        # Create combined query
        combined_query_str = "\n".join(query_parts)
        try:
            self.combined_query = tree_sitter.Query(language, combined_query_str)
        except Exception:
            # Fallback: just use highlights query if combination fails
            self.combined_query = tree_sitter.Query(language, highlights_query)
            self.locals_pattern_index = 0
            self.highlights_pattern_index = 0

        # Keep individual queries for backwards compatibility
        self.highlights_query = tree_sitter.Query(language, highlights_query)
        self.injections_query = (
            tree_sitter.Query(language, injections_query) if injections_query else None
        )
        self.locals_query = (
            tree_sitter.Query(language, locals_query) if locals_query else None
        )

        # Extract highlight names from queries if not provided
        if highlight_names is None:
            self.highlight_names = self._extract_capture_names()
        else:
            self.highlight_names = highlight_names

        # Build capture name to index mapping
        self.capture_index_map: Dict[str, int] = {
            name: idx for idx, name in enumerate(self.highlight_names)
        }

        # Track patterns that shouldn't match local variables
        self.non_local_variable_patterns = set()

    def _extract_capture_names(self) -> List[str]:
        """Extract unique capture names from all queries.

        Returns the complete DEFAULT_HIGHLIGHT_NAMES list to match the
        Rust tree-sitter-highlight library's behavior. This ensures that
        highlight indices are consistent between Python and Rust implementations.

        Query captures that don't match any standard name (directly or hierarchically)
        are ignored during highlighting via the hierarchical resolution in the highlighter.

        Returns:
            Complete list of standard highlight names
        """
        # Always return the complete standard list to ensure consistent indices
        # Captures in queries that don't match these names will be handled via
        # hierarchical matching in the highlighter (_resolve_highlight_index)
        return list(DEFAULT_HIGHLIGHT_NAMES)

    @classmethod
    def from_language_path(
        cls,
        language: tree_sitter.Language,
        language_path: Path,
    ) -> "HighlightConfiguration":
        """Create configuration from a language directory.

        Expects the directory to contain:
        - highlights.scm (required)
        - injections.scm (optional)
        - locals.scm (optional)

        Uses the standard DEFAULT_HIGHLIGHT_NAMES list to match
        the behavior of the Rust tree-sitter-highlight library.

        Args:
            language: Tree-sitter Language for parsing
            language_path: Path to directory containing .scm query files

        Returns:
            HighlightConfiguration instance

        Raises:
            FileNotFoundError: If highlights.scm is not found
        """
        highlights_path = language_path / "highlights.scm"
        if not highlights_path.exists():
            raise FileNotFoundError(
                f"Required highlights.scm not found at {highlights_path}"
            )

        highlights_query = highlights_path.read_text()

        injections_path = language_path / "injections.scm"
        injections_query = (
            injections_path.read_text() if injections_path.exists() else None
        )

        locals_path = language_path / "locals.scm"
        locals_query = locals_path.read_text() if locals_path.exists() else None

        # Auto-extract highlight names (will be ordered with standard names first)
        return cls(
            language=language,
            highlights_query=highlights_query,
            injections_query=injections_query,
            locals_query=locals_query,
        )
