"""Command-line interface for TSColor using Click."""

import sys
from pathlib import Path

import click

from . import Highlighter, __version__, get_theme, list_themes
from .formatters import AnsiFormatter, HtmlFormatter
from .languages import detect_language, get_configuration, load_language_parser


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="""
\b
Examples:
  # Highlight a Python file with Dracula theme
  tscolor script.py

  # Highlight with a specific theme
  tscolor --theme monokai script.py

  # Highlight and save as HTML
  tscolor --output output.html script.py

  # Specify language explicitly
  tscolor --language python file.txt

  # List all available themes
  tscolor --list-themes

  # Include background color in terminal output
  tscolor --background script.py
""",
)
@click.version_option(version=__version__, prog_name="tscolor")
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
    show_default=True,
    help="Color theme",
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
    "list_themes_flag",
    is_flag=True,
    help="List all available themes",
)
def main(
    file: Path | None,
    language: str | None,
    theme: str,
    output: Path | None,
    background: bool,
    list_themes_flag: bool,
) -> None:
    """Syntax highlighting using tree-sitter.

    Highlight source code files with syntax highlighting powered by tree-sitter.
    Supports multiple languages and themes, with output to terminal (ANSI colors)
    or HTML files.
    """
    # Handle list-themes flag
    if list_themes_flag:
        show_themes()
        return

    # Require file if not listing themes
    if file is None:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit(0)

    # At this point, file is guaranteed to be not None
    assert file is not None  # Type narrowing for type checker

    # Highlight the file
    exit_code = highlight_file(
        file_path=file,
        language=language,
        theme_name=theme,
        output=output,
        background=background,
    )
    if exit_code != 0:
        ctx = click.get_current_context()
        ctx.exit(exit_code)


def show_themes() -> None:
    """List all available themes."""
    from . import get_theme_info

    click.echo("Available themes:")
    click.echo()

    # List dark themes
    dark_themes = list_themes(category="dark")
    if dark_themes:
        click.echo("Dark themes:")
        for name in dark_themes:
            info = get_theme_info(name)
            author = f" by {info['author']}" if info["author"] else ""
            click.echo(f"  • {name}{author}")
        click.echo()

    # List light themes
    light_themes = list_themes(category="light")
    if light_themes:
        click.echo("Light themes:")
        for name in light_themes:
            info = get_theme_info(name)
            author = f" by {info['author']}" if info["author"] else ""
            click.echo(f"  • {name}{author}")
        click.echo()


def highlight_file(
    file_path: Path,
    language: str | None = None,
    theme_name: str = "dracula",
    output: Path | None = None,
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
            click.echo(
                f"Error: Could not detect language for {file_path.suffix}",
                err=True,
            )
            click.echo("Please specify language with --language", err=True)
            return 1

    # Load language parser
    if not load_language_parser(language):
        click.echo(
            f"Error: Could not load parser for language: {language}",
            err=True,
        )
        click.echo(
            f"Make sure tree-sitter-{language} is installed:",
            err=True,
        )
        click.echo(f"  pip install tree-sitter-{language}", err=True)
        return 1

    # Get language configuration
    try:
        config = get_configuration(language)
    except (FileNotFoundError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        return 1

    # Get theme
    try:
        theme = get_theme(theme_name)
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        available = ", ".join(list_themes())
        click.echo(f"Available themes: {available}", err=True)
        return 1

    # Read source file
    try:
        source = file_path.read_bytes()
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
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
            click.echo(f"HTML output saved to: {output}")
        else:
            # Print to terminal with ANSI colors
            formatter = AnsiFormatter(theme)
            if background:
                colored = formatter.format_with_background(source, events, config)
            else:
                colored = formatter.format(source, events, config)
            # Use sys.stdout.write to preserve ANSI codes
            sys.stdout.write(colored)
            sys.stdout.write("\n")

        return 0

    except Exception as e:
        click.echo(f"Error during highlighting: {e}", err=True)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()
