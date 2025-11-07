"""Language support for tree-sitter highlighting."""

import json
from pathlib import Path
from typing import Dict, Optional
import tree_sitter
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

from ..configuration import HighlightConfiguration

# Mapping from pygments lexer names to tree-sitter language names
# Only for languages we currently support
PYGMENTS_TO_TSCOLOR: Dict[str, str] = {
    "Python": "python",
    "Python3": "python",
    "JavaScript": "javascript",
    "Matlab": "matlab",
}

# Map of language names to package names (only supported languages)
LANGUAGE_PACKAGES: Dict[str, str] = {
    "python": "tree_sitter_python",
    "javascript": "tree_sitter_javascript",
    "matlab": "tree_sitter_matlab",
}


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
        self._file_extensions: Dict[str, str] = {}  # extension -> language name
        self._load_file_extensions()

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
            raise FileNotFoundError(f"Language directory not found: {language_path}")

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

    def _load_file_extensions(self) -> None:
        """Load file extensions from tree-sitter.json files."""
        for lang_dir in self.languages_dir.iterdir():
            if not lang_dir.is_dir():
                continue

            tree_sitter_json = lang_dir / "tree-sitter.json"
            if not tree_sitter_json.exists():
                continue

            try:
                with tree_sitter_json.open() as f:
                    config = json.load(f)
                    file_types = config.get("file-types", [])
                    lang_name = lang_dir.name

                    # Map each extension to the language name
                    for ext in file_types:
                        # Store with leading dot for consistency
                        ext_with_dot = f".{ext}" if not ext.startswith(".") else ext
                        self._file_extensions[ext_with_dot] = lang_name
            except (json.JSONDecodeError, OSError):
                # Skip languages with invalid or unreadable config
                continue

    def detect_language_by_extension(self, file_path: Path) -> Optional[str]:
        """Detect language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name or None if not detected
        """
        extension = file_path.suffix.lower()
        return self._file_extensions.get(extension)

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect language from file content using pygments, with fallback to extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name or None if not detected
        """
        # First try pygments for supported languages (python, javascript, matlab)
        try:
            content = file_path.read_text(errors="ignore")
            lexer = guess_lexer(content)
            lexer_name = lexer.name

            # Map pygments lexer name to tree-sitter language name
            lang = PYGMENTS_TO_TSCOLOR.get(lexer_name)
            if lang:
                return lang
        except (ClassNotFound, Exception):
            # If pygments fails, continue to extension-based detection
            pass

        # Fallback to file extension detection
        return self.detect_language_by_extension(file_path)

    def load_language_parser(self, language: str) -> bool:
        """Dynamically load and register a language parser.

        Args:
            language: Language name

        Returns:
            True if successful, False otherwise
        """
        package_name = LANGUAGE_PACKAGES.get(language)
        if not package_name:
            return False

        try:
            # Dynamically import the language module
            module = __import__(package_name, fromlist=["language"])
            lang_capsule = module.language()  # type: ignore[attr-defined]
            # Register will handle wrapping the capsule in Language
            self.register_language(language, lang_capsule)
            return True
        except ImportError:
            return False


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


def detect_language_by_extension(file_path: Path) -> Optional[str]:
    """Detect language by file extension using the default registry.

    Args:
        file_path: Path to the file

    Returns:
        Language name or None if not detected
    """
    return _default_registry.detect_language_by_extension(file_path)


def detect_language(file_path: Path) -> Optional[str]:
    """Detect language from file content using the default registry.

    Args:
        file_path: Path to the file

    Returns:
        Language name or None if not detected
    """
    return _default_registry.detect_language(file_path)


def load_language_parser(language: str) -> bool:
    """Dynamically load and register a language parser using the default registry.

    Args:
        language: Language name

    Returns:
        True if successful, False otherwise
    """
    return _default_registry.load_language_parser(language)
