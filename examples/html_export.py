"""Example of exporting syntax-highlighted code to HTML."""

try:
    import tree_sitter_python as ts_python
except ImportError:
    print("Please install tree-sitter-python: pip install tree-sitter-python")
    exit(1)

from pathlib import Path
from tscolor import Highlighter, get_theme
from tscolor.languages import register_language, get_configuration
from tscolor.formatters import HtmlFormatter

# Sample Python code to highlight
source_code = b"""
class Calculator:
    '''A simple calculator class.'''

    def __init__(self):
        self.result = 0

    def add(self, x, y):
        '''Add two numbers.'''
        self.result = x + y
        return self.result

    def multiply(self, x, y):
        '''Multiply two numbers.'''
        self.result = x * y
        return self.result

# Create and use the calculator
calc = Calculator()
print(f"5 + 3 = {calc.add(5, 3)}")
print(f"5 * 3 = {calc.multiply(5, 3)}")
"""


def main():
    # Register the Python language
    print("Registering Python language...")
    register_language("python", ts_python.language())

    # Get configuration and theme
    config = get_configuration("python")
    theme = get_theme("dracula")

    # Create highlighter
    highlighter = Highlighter()

    # Highlight the code
    print("Highlighting code...")
    events = highlighter.highlight(config, source_code)

    # Create HTML formatter
    html_formatter = HtmlFormatter(theme)

    # Generate complete HTML document
    html = html_formatter.format_complete(
        source_code,
        events,
        config,
        title="Python Calculator Example - Highlighted with TSColor",
    )

    # Save to file
    output_path = Path("highlighted_code.html")
    output_path.write_text(html)

    print(f"\nHTML file generated: {output_path.absolute()}")
    print("Open it in a web browser to see the highlighted code!")

    # Also generate a CSS stylesheet
    css = html_formatter.generate_css(config)
    css_path = Path("syntax_highlight.css")
    css_path.write_text(css)

    print(f"CSS stylesheet generated: {css_path.absolute()}")


if __name__ == "__main__":
    main()
