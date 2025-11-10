"""TSColor - Pure Python implementation of tree-sitter-highlight.

This package provides syntax highlighting using tree-sitter parsers with
support for multiple languages and themes.

Example:
    >>> from tscolor import Highlighter, get_theme
    >>> from tscolor.languages import register_language, get_configuration
    >>> from tscolor.formatters import AnsiFormatter
    >>> import tree_sitter_python as ts_python
    >>>
    >>> # Register a language
    >>> register_language("python", ts_python.language())
    >>>
    >>> # Get configuration and theme
    >>> config = get_configuration("python")
    >>> theme = get_theme("dracula")
    >>>
    >>> # Highlight code
    >>> highlighter = Highlighter()
    >>> source = b"def hello(): pass"
    >>> events = highlighter.highlight(config, source)
    >>>
    >>> # Format output
    >>> formatter = AnsiFormatter(theme)
    >>> print(formatter.format(source, highlighter.highlight(config, source), config))
"""

__version__ = "0.1.0"

# Import the main highlighter
from .highlighter import Highlighter
from .configuration import HighlightConfiguration
from .theme import (
    Theme,
    get_theme,
    list_themes,
    register_theme,
    get_theme_info,
    THEMES,
)
from .events import (
    HighlightEvent,
    SourceEvent,
    HighlightStartEvent,
    HighlightEndEvent,
)
from .scope import LocalScope, LocalDefinition, ScopeStack
from .layer import HighlightLayer

__all__ = [
    "Highlighter",
    "HighlightConfiguration",
    "Theme",
    "get_theme",
    "list_themes",
    "register_theme",
    "get_theme_info",
    "THEMES",
    "HighlightEvent",
    "SourceEvent",
    "HighlightStartEvent",
    "HighlightEndEvent",
    "LocalScope",
    "LocalDefinition",
    "ScopeStack",
    "HighlightLayer",
    "__version__",
]
