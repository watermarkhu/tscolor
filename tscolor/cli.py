"""Command-line interface for TSColor using argparse."""
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict

from . import Highlighter, get_theme, list_themes, __version__
from .languages import register_language, get_configuration
from .formatters import AnsiFormatter, HtmlFormatter


# Language mapping from file extension to language name
LANGUAGE_EXTENSIONS: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".html": "html",
    ".xml": "xml",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".md": "markdown",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
}


def detect_language(file_path: Path) -> Optional[str]:
    """Detect language from file extension.

    Args:
        file_path: Path to the file

    Returns:
        Language name or None if not detected
    """
    extension = file_path.suffix.lower()
    return LANGUAGE_EXTENSIONS.get(extension)


def load_language_parser(language: str) -> bool:
    """Dynamically load and register a language parser.

    Args:
        language: Language name

    Returns:
        True if successful, False otherwise
    """
    # Map of language names to package names
    package_map = {
        "python": "tree_sitter_python",
        "javascript": "tree_sitter_javascript",
        "typescript": "tree_sitter_typescript",
        "rust": "tree_sitter_rust",
        "go": "tree_sitter_go",
        "c": "tree_sitter_c",
        "cpp": "tree_sitter_cpp",
        "java": "tree_sitter_java",
        "ruby": "tree_sitter_ruby",
        "php": "tree_sitter_php",
        "swift": "tree_sitter_swift",
        "kotlin": "tree_sitter_kotlin",
        "scala": "tree_sitter_scala",
        "html": "tree_sitter_html",
        "css": "tree_sitter_css",
        "json": "tree_sitter_json",
        "bash": "tree_sitter_bash",
    }

    package_name = package_map.get(language)
    if not package_name:
        return False

    try:
        # Dynamically import the language module
        module = __import__(package_name, fromlist=["language"])
        lang_capsule = module.language()
        # Register will handle wrapping the capsule in Language
        register_language(language, lang_capsule)
        return True
    except ImportError:
        return False


def highlight_file(
    file_path: Path,
    language: Optional[str] = None,
    theme_name: str = "dracula",
    output: Optional[Path] = None,
    background: bool = False,
) -> int:
    """Highlight a source file and print to terminal or save as HTML.

    Args:
        file_path: Path to the file to highlight
        language: Language name (auto-detected if None)
        theme_name: Theme name
        output: Optional output path for HTML
        background: Whether to include background color in terminal output

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Detect language if not specified
    if language is None:
        language = detect_language(file_path)
        if language is None:
            print(
                f"Error: Could not detect language for {file_path.suffix}",
                file=sys.stderr,
            )
            print("Please specify language with --language", file=sys.stderr)
            return 1

    # Load language parser
    if not load_language_parser(language):
        print(
            f"Error: Could not load parser for language: {language}",
            file=sys.stderr,
        )
        print(
            f"Make sure tree-sitter-{language} is installed:",
            file=sys.stderr,
        )
        print(f"  pip install tree-sitter-{language}", file=sys.stderr)
        return 1

    # Get language configuration
    try:
        config = get_configuration(language)
    except (FileNotFoundError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Get theme
    try:
        theme = get_theme(theme_name)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        available = ", ".join(list_themes())
        print(f"Available themes: {available}", file=sys.stderr)
        return 1

    # Read source file
    try:
        source = file_path.read_bytes()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Highlight the code
    highlighter = Highlighter()
    try:
        events = highlighter.highlight(config, source)

        if output:
            # Generate HTML output
            formatter = HtmlFormatter(theme)
            html = formatter.format_complete(
                source,
                events,
                config,
                title=f"{file_path.name} - Highlighted with TSColor",
            )
            output.write_text(html)
            print(f"HTML output saved to: {output}")
        else:
            # Print to terminal with ANSI colors
            formatter = AnsiFormatter(theme)
            if background:
                colored = formatter.format_with_background(source, events, config)
            else:
                colored = formatter.format(source, events, config)
            print(colored)

        return 0

    except Exception as e:
        print(f"Error during highlighting: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


def list_themes_cmd() -> int:
    """List all available themes.

    Returns:
        Exit code (always 0)
    """
    from . import get_theme_info

    print("Available themes:")
    print()

    # List dark themes
    dark_themes = list_themes(category="dark")
    if dark_themes:
        print("Dark themes:")
        for name in dark_themes:
            info = get_theme_info(name)
            author = f" by {info['author']}" if info["author"] else ""
            print(f"  • {name}{author}")
        print()

    # List light themes
    light_themes = list_themes(category="light")
    if light_themes:
        print("Light themes:")
        for name in light_themes:
            info = get_theme_info(name)
            author = f" by {info['author']}" if info["author"] else ""
            print(f"  • {name}{author}")
        print()

    return 0


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="tscolor",
        description="Syntax highlighting using tree-sitter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # Highlight a Python file with Dracula theme
  tscolor script.py

  # Highlight with a specific theme
  tscolor script.py --theme monokai

  # Highlight and save as HTML
  tscolor script.py --output output.html

  # Specify language explicitly
  tscolor file.txt --language python

  # List all available themes
  tscolor --list-themes

  # Include background color in terminal output
  tscolor script.py --background
        """,
    )

    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Source code file to highlight",
    )

    parser.add_argument(
        "-l",
        "--language",
        type=str,
        help="Programming language (auto-detected from extension if not specified)",
    )

    parser.add_argument(
        "-t",
        "--theme",
        type=str,
        default="dracula",
        help="Color theme (default: dracula)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output HTML file (prints to terminal if not specified)",
    )

    parser.add_argument(
        "-b",
        "--background",
        action="store_true",
        help="Include background color in terminal output",
    )

    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List all available themes",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Handle list-themes flag
    if args.list_themes:
        sys.exit(list_themes_cmd())

    # Require file argument if not listing themes
    if args.file is None:
        parser.print_help()
        sys.exit(0)

    # Check if file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Highlight the file
    exit_code = highlight_file(
        file_path=args.file,
        language=args.language,
        theme_name=args.theme,
        output=args.output,
        background=args.background,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
