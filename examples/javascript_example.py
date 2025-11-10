"""Example of highlighting JavaScript code."""

try:
    import tree_sitter_javascript as ts_javascript
except ImportError:
    print("Please install tree-sitter-javascript: pip install tree-sitter-javascript")
    exit(1)

from tscolor import Highlighter, get_theme
from tscolor.languages import register_language, get_configuration
from tscolor.formatters import AnsiFormatter

# Sample JavaScript code to highlight
source_code = b"""
// Calculate fibonacci numbers
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Test the function
const numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
numbers.forEach(num => {
    console.log(`fibonacci(${num}) = ${fibonacci(num)}`);
});

// ES6 arrow function version
const fibonacciArrow = (n) => n <= 1 ? n : fibonacciArrow(n - 1) + fibonacciArrow(n - 2);
"""


def main():
    # Register the JavaScript language
    print("Registering JavaScript language...")
    register_language("javascript", ts_javascript.language())

    # Get configuration and theme
    print("Loading configuration and theme...")
    config = get_configuration("javascript")
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
    print("Highlighted JavaScript Code (Dracula Theme)")
    print("=" * 60)
    print(colored_code)
    print("=" * 60)


if __name__ == "__main__":
    main()
