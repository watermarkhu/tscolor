"""Simple example of syntax highlighting with TSColor."""

# Note: This example requires tree-sitter-python to be installed
# pip install tree-sitter-python

try:
    import tree_sitter_python as ts_python
except ImportError:
    print("Please install tree-sitter-python: pip install tree-sitter-python")
    exit(1)

from tscolor import Highlighter, get_theme
from tscolor.languages import register_language, get_configuration
from tscolor.formatters import AnsiFormatter

# Sample Python code to highlight
source_code = b"""
def factorial(n):
    '''Calculate factorial of n.'''
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test the function
print(factorial(5))
"""

def main():
    # Register the Python language
    print("Registering Python language...")
    register_language("python", ts_python.language())

    # Get configuration and theme
    print("Loading configuration and theme...")
    config = get_configuration("python")
    theme = get_theme("dracula")

    # Create highlighter
    highlighter = Highlighter()

    # Highlight the code
    print("Highlighting code...")
    events = highlighter.highlight(config, source_code)

    # Format for terminal output
    formatter = AnsiFormatter(theme)
    colored_code = formatter.format(source_code, events, config)

    # Display the highlighted code
    print("\n" + "=" * 60)
    print("Highlighted Python Code (Dracula Theme)")
    print("=" * 60)
    print(colored_code)
    print("=" * 60)


if __name__ == "__main__":
    main()
