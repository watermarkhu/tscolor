"""Language support for tree-sitter highlighting."""
from pathlib import Path
from typing import Dict, Optional
import tree_sitter

from ..configuration import HighlightConfiguration


class LanguageRegistry:
    """Registry for loading and managing language configurations.

    This class helps manage tree-sitter languages and their associated
    query files (highlights.scm, injections.scm, locals.scm).
    """

    def __init__(self, languages_dir: Optional[Path] = None):
        """Initialize the language registry.

        Args:
            languages_dir: Directory containing language subdirectories.
                          If None, uses the package's languages directory.
        """
        if languages_dir is None:
            languages_dir = Path(__file__).parent
        self.languages_dir = languages_dir
        self._languages: Dict[str, tree_sitter.Language] = {}

    def register_language(
        self,
        name: str,
        language,
    ) -> None:
        """Register a tree-sitter language.

        Args:
            name: Language name (e.g., "python", "javascript")
            language: Tree-sitter Language instance or language capsule
        """
        # Wrap capsule in Language if needed
        if not isinstance(language, tree_sitter.Language):
            language = tree_sitter.Language(language)
        self._languages[name] = language

    def get_configuration(self, name: str) -> HighlightConfiguration:
        """Get highlight configuration for a language.

        Args:
            name: Language name

        Returns:
            HighlightConfiguration instance

        Raises:
            KeyError: If language is not registered
            FileNotFoundError: If language query files not found
        """
        if name not in self._languages:
            raise KeyError(
                f"Language '{name}' not registered. "
                f"Available languages: {', '.join(self._languages.keys())}"
            )

        language = self._languages[name]
        language_path = self.languages_dir / name

        if not language_path.exists():
            raise FileNotFoundError(
                f"Language directory not found: {language_path}"
            )

        return HighlightConfiguration.from_language_path(
            language=language,
            language_path=language_path,
        )

    def list_languages(self) -> list:
        """List all registered languages.

        Returns:
            List of language names
        """
        return list(self._languages.keys())


# Global language registry
_default_registry = LanguageRegistry()


def register_language(name: str, language) -> None:
    """Register a language in the default registry.

    Args:
        name: Language name
        language: Tree-sitter Language instance or language capsule
    """
    # Wrap capsule in Language if needed
    if not isinstance(language, tree_sitter.Language):
        language = tree_sitter.Language(language)
    _default_registry.register_language(name, language)


def get_configuration(name: str) -> HighlightConfiguration:
    """Get configuration from the default registry.

    Args:
        name: Language name

    Returns:
        HighlightConfiguration instance
    """
    return _default_registry.get_configuration(name)


def list_languages() -> list:
    """List languages in the default registry.

    Returns:
        List of language names
    """
    return _default_registry.list_languages()
