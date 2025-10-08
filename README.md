# tscolor

A fast Python syntax highlighting library powered by [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) with Rust performance.

## Features

- **Fast**: Core highlighting logic implemented in Rust
- **Multiple output formats**: Terminal (ANSI colors) and HTML
- **Multiple themes**: Dark and light themes included
- **Extensible**: Support for multiple programming languages via optional features
- **Tree-sitter powered**: Uses official tree-sitter grammars for accurate syntax highlighting

## Installation

Install the base package:

```bash
pip install tscolor
```

Install with specific language support:

```bash
# Python support
pip install tscolor[python]

# Rust support
pip install tscolor[rust]

# JavaScript support
pip install tscolor[javascript]

# JSON support
pip install tscolor[json]

# All languages
pip install tscolor[all-languages]
```

## Usage

### Basic Usage

```python
import tscolor

# Highlight Python code for terminal output
code = """
def hello(name):
    print(f"Hello, {name}!")
"""

# Terminal output with ANSI colors (dark theme)
highlighted = tscolor.highlight(code, "python", "terminal", "dark")
print(highlighted)

# HTML output (light theme)
html = tscolor.highlight(code, "python", "html", "light")
print(html)
```

### API Reference

#### `highlight(code, language, output_format="terminal", theme_name="dark")`

Highlight source code and return formatted output.

**Parameters:**
- `code` (str): The source code to highlight
- `language` (str): Programming language (e.g., "python", "rust", "javascript", "json")
- `output_format` (str): Output format - "terminal" or "html" (default: "terminal")
- `theme_name` (str): Theme name - "dark" or "light" (default: "dark")

**Returns:** Highlighted code as a string

**Example:**
```python
result = tscolor.highlight(code, "python", "terminal", "dark")
```

#### `get_available_languages()`

Get list of available programming languages based on installed features.

**Returns:** List of language names (e.g., `["python", "rust", "javascript", "json"]`)

**Example:**
```python
languages = tscolor.get_available_languages()
print(f"Supported languages: {languages}")
```

#### `get_available_themes()`

Get list of available themes.

**Returns:** List of theme names (e.g., `["dark", "light"]`)

**Example:**
```python
themes = tscolor.get_available_themes()
print(f"Available themes: {themes}")
```

## Supported Languages

Languages are available as optional features. Install the package with the appropriate extras to enable support:

- `python` - Python syntax highlighting
- `rust` - Rust syntax highlighting  
- `javascript` - JavaScript syntax highlighting
- `json` - JSON syntax highlighting
- `all-languages` - All supported languages

## Themes

### Dark Theme (default)
Optimized for dark terminal backgrounds with vibrant colors.

### Light Theme
Optimized for light backgrounds with muted colors.

## Development

### Building from Source

Requirements:
- Rust toolchain (1.70+)
- Python 3.8+
- maturin

```bash
# Clone the repository
git clone https://github.com/watermarkhu/tscolor.git
cd tscolor

# Build with all features
maturin build --release --features all-languages

# Install in development mode
maturin develop --features all-languages
```

### Running Examples

```bash
python example.py
```

## Architecture

- **Rust Core**: Fast syntax highlighting using tree-sitter
- **Python Bindings**: Exposed via PyO3 for seamless Python integration
- **Optional Features**: Languages are compiled as Rust features and mapped to Python optional dependencies

## License

BSD 3-Clause License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.