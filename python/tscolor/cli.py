#!/usr/bin/env python3
"""
Python CLI for tscolor syntax highlighting.
"""
import argparse
import sys
from pathlib import Path

try:
    import tscolor
except ImportError:
    print("Error: tscolor package not found. Make sure it's installed.", file=sys.stderr)
    sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="A syntax highlighter using tree-sitter",
        prog="tscolor"
    )
    
    parser.add_argument(
        "file",
        type=Path,
        help="Input file path to highlight"
    )
    
    parser.add_argument(
        "language",
        nargs='?',
        help="Programming language (e.g., python, rust, javascript, json). If not provided, will be auto-detected from file extension."
    )
    
    parser.add_argument(
        "--html",
        type=Path,
        help="Output HTML to file instead of terminal"
    )
    
    parser.add_argument(
        "--theme",
        default="dark",
        help="Theme to use (default: dark)"
    )
    
    args = parser.parse_args()
    
    # Auto-detect language if not provided
    language = args.language
    if language is None:
        language = tscolor.detect_language(str(args.file))
        if language is None:
            print(f"Error: Could not auto-detect language for '{args.file}'. Please specify the language explicitly.", file=sys.stderr)
            print(f"Supported extensions: .py, .pyw, .rs, .js, .jsx, .mjs, .cjs, .json, .jsonc", file=sys.stderr)
            sys.exit(1)
        print(f"Auto-detected language: {language}")
    
    # Read the input file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check if language is available
    try:
        available_languages = tscolor.get_available_languages()
        if language not in available_languages:
            print(f"Language '{language}' is not available. Available languages: {', '.join(available_languages)}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error getting available languages: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check if theme is available
    try:
        available_themes = tscolor.get_available_themes()
        if args.theme not in available_themes:
            print(f"Theme '{args.theme}' is not available. Available themes: {', '.join(available_themes)}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error getting available themes: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output format
    output_format = "html" if args.html else "terminal"
    
    # Highlight the code
    try:
        result = tscolor.highlight(code, language, output_format, args.theme)
    except Exception as e:
        print(f"Error highlighting code: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output the result
    if args.html:
        try:
            with open(args.html, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"HTML output written to: {args.html}")
        except Exception as e:
            print(f"Error writing HTML file '{args.html}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(result, end='')


if __name__ == "__main__":
    main()