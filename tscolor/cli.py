"""Command-line interface for TSColor using Click."""
import sys
from pathlib import Path
from typing import Optional, Dict

import click

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
        lang_obj = module.language()
        register_language(language, lang_obj)
        return True
    except ImportError:
        return False


@click.group(invoke_without_command=True)
@click.argument("file", type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    "-l",
    "--language",
    type=str,
    help="Programming language (auto-detected from extension if not specified)",
)
@click.option(
    "-t",
    "--theme",
    type=str,
    default="dracula",
    help="Color theme (default: dracula)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output HTML file (prints to terminal if not specified)",
)
@click.option(
    "-b",
    "--background",
    is_flag=True,
    help="Include background color in terminal output",
)
@click.option(
    "--list-themes",
    is_flag=True,
    help="List all available themes",
)
@click.version_option(version=__version__, prog_name="tscolor")
@click.pass_context
def cli(
    ctx: click.Context,
    file: Optional[Path],
    language: Optional[str],
    theme: str,
    output: Optional[Path],
    background: bool,
    list_themes_flag: bool,
):
    """Syntax highlighting using tree-sitter.

    Highlight source code files with beautiful colors in your terminal or export to HTML.

    \b
    Examples:
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
    """
    # If no command is invoked, handle the default behavior
    if ctx.invoked_subcommand is None:
        if list_themes_flag:
            list_themes_cmd()
        elif file:
            highlight_file(file, language, theme, output, background)
        else:
            click.echo(ctx.get_help())


@cli.command(name="themes")
def list_themes_command():
    """List all available themes."""
    list_themes_cmd()


@cli.command(name="highlight")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-l",
    "--language",
    type=str,
    help="Programming language (auto-detected from extension if not specified)",
)
@click.option(
    "-t",
    "--theme",
    type=str,
    default="dracula",
    help="Color theme",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output HTML file",
)
@click.option(
    "-b",
    "--background",
    is_flag=True,
    help="Include background color in terminal output",
)
def highlight_command(
    file: Path,
    language: Optional[str],
    theme: str,
    output: Optional[Path],
    background: bool,
):
    """Highlight a source code file."""
    highlight_file(file, language, theme, output, background)


def highlight_file(
    file_path: Path,
    language: Optional[str] = None,
    theme_name: str = "dracula",
    output: Optional[Path] = None,
    background: bool = False,
) -> None:
    """Highlight a source file and print to terminal or save as HTML.

    Args:
        file_path: Path to the file to highlight
        language: Language name (auto-detected if None)
        theme_name: Theme name
        output: Optional output path for HTML
        background: Whether to include background color in terminal output
    """
    # Detect language if not specified
    if language is None:
        language = detect_language(file_path)
        if language is None:
            click.secho(
                f"Error: Could not detect language for {file_path.suffix}",
                fg="red",
                err=True,
            )
            click.echo("Please specify language with --language", err=True)
            sys.exit(1)

    # Load language parser
    if not load_language_parser(language):
        click.secho(
            f"Error: Could not load parser for language: {language}",
            fg="red",
            err=True,
        )
        click.echo(
            f"Make sure tree-sitter-{language} is installed:", err=True
        )
        click.echo(f"  pip install tree-sitter-{language}", err=True)
        sys.exit(1)

    # Get language configuration
    try:
        config = get_configuration(language)
    except (FileNotFoundError, KeyError) as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)

    # Get theme
    try:
        theme = get_theme(theme_name)
    except KeyError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        available = ", ".join(list_themes())
        click.echo(f"Available themes: {available}", err=True)
        sys.exit(1)

    # Read source file
    try:
        source = file_path.read_bytes()
    except Exception as e:
        click.secho(f"Error reading file: {e}", fg="red", err=True)
        sys.exit(1)

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
            click.secho(f"HTML output saved to: {output}", fg="green")
        else:
            # Print to terminal with ANSI colors
            formatter = AnsiFormatter(theme)
            if background:
                colored = formatter.format_with_background(source, events, config)
            else:
                colored = formatter.format(source, events, config)
            click.echo(colored)

    except Exception as e:
        click.secho(f"Error during highlighting: {e}", fg="red", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


def list_themes_cmd() -> None:
    """List all available themes."""
    from . import get_theme_info

    click.secho("Available themes:", bold=True)
    click.echo()

    # List dark themes
    dark_themes = list_themes(category="dark")
    if dark_themes:
        click.secho("Dark themes:", fg="cyan", bold=True)
        for name in dark_themes:
            info = get_theme_info(name)
            author = f" by {info['author']}" if info["author"] else ""
            click.echo(f"  • {click.style(name, fg='green')}{author}")
        click.echo()

    # List light themes
    light_themes = list_themes(category="light")
    if light_themes:
        click.secho("Light themes:", fg="yellow", bold=True)
        for name in light_themes:
            info = get_theme_info(name)
            author = f" by {info['author']}" if info["author"] else ""
            click.echo(f"  • {click.style(name, fg='green')}{author}")
        click.echo()


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
