#!/usr/bin/env python3
"""
Example usage of tscolor - tree-sitter based syntax highlighting
"""

import tscolor

def main():
    # Get available languages and themes
    print("Available languages:", tscolor.get_available_languages())
    print("Available themes:", tscolor.get_available_themes())
    print()

    # Example Python code
    python_code = """
def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number\"\"\"
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Calculate and print first 10 Fibonacci numbers
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""

    # Highlight for terminal output (dark theme)
    print("=== Terminal Output (Dark Theme) ===")
    terminal_output = tscolor.highlight(python_code, "python", "terminal", "dark")
    print(terminal_output)
    print()

    # Highlight for HTML output (light theme)
    print("=== HTML Output (Light Theme) ===")
    html_output = tscolor.highlight(python_code, "python", "html", "light")
    print(html_output)
    print()

    # Example with different language (if rust feature is enabled)
    try:
        rust_code = """
fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    let sum: i32 = numbers.iter().sum();
    println!("Sum: {}", sum);
}
"""
        print("=== Rust Code (Terminal, Dark Theme) ===")
        rust_output = tscolor.highlight(rust_code, "rust", "terminal", "dark")
        print(rust_output)
    except RuntimeError as e:
        print(f"Rust language not available: {e}")

if __name__ == "__main__":
    main()
