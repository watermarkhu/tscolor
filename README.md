# tscolor

A fast syntax highlighting library and command-line tool powered by [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) with Rust performance.

## Features

- **Fast**: Core highlighting logic implemented in Rust
- **Multiple output formats**: Terminal (ANSI colors) and HTML
- **Multiple themes**: Dark and light themes included
- **Command-line interface**: Highlight files directly from the terminal
- **Python library**: Full Python API for integration into applications
- **Extensible**: Support for multiple programming languages via optional features
- **Tree-sitter powered**: Uses official tree-sitter grammars for accurate syntax highlighting

## Installation

### Quick Start (All Languages)

Install the package with all language support (recommended):

```bash
pip install tscolor
# or
uv add tscolor
```

### Optional Dependencies (Semantic)

The package includes optional dependency markers for semantic versioning:

```bash
# These all install the same wheel (with all languages)
# But declare your intent for dependency resolution
pip install tscolor[python]
pip install tscolor[javascript]
pip install tscolor[all-languages]
```

**Note**: All pre-built wheels include all language support by default. The optional dependencies are semantic markers that can be used in your project's dependencies to indicate which language features your code uses.

## Usage

### Command Line Interface

After building the project (see [Building from Source](#building-from-source)), you can use `tscolor` as a command-line tool:

```bash
# Highlight a Python file to terminal (with ANSI colors)
./target/release/tscolor example.py python

# Highlight with light theme
./target/release/tscolor example.py python --theme light

# Output to HTML file
./target/release/tscolor example.py python --html output.html

# Show help
./target/release/tscolor --help
```

#### CLI Options

- `<FILE>`: Input file path to highlight
- `<LANGUAGE>`: Programming language (python, rust, javascript, json)
- `--html <FILE>`: Output HTML to file instead of terminal
- `--theme <THEME>`: Theme to use (built-in: dark, light; or any custom theme from `themes/` directory, default: dark)

The CLI automatically discovers themes from JSON files in the `themes/` directory, making it easy to add and use custom themes.

#### Using CLI with uv

```bash
# Install the package with uv
uv add tscolor

# Use the CLI through uv
uv run tscolor myfile.py python
uv run tscolor myfile.py python --theme light
uv run tscolor myfile.py python --html output.html
```

#### Install CLI Globally (Rust binary)

```bash
# Build the release binary
cargo build --release --features all-languages

# Install system-wide (requires sudo)
sudo cp target/release/tscolor /usr/local/bin/

# Now you can use tscolor from anywhere
tscolor myfile.py python
```

### Python Library Usage

#### Basic Usage

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

### Built-in Themes

- **Dark Theme (default)**: Optimized for dark terminal backgrounds with vibrant colors
- **Light Theme**: Optimized for light backgrounds with muted colors

### Custom Themes

You can easily add custom themes by creating JSON files in the `themes/` directory. Each theme file should follow this format:

```json
{
  "name": "my_theme",
  "description": "My custom theme description",
  "colors": {
    "comment": "#808080",
    "string": "#98c379",
    "number": "#d19a66",
    "keyword": "#c678dd",
    "function": "#61afef",
    "type": "#e5c07b",
    "variable": "#e06c75",
    "operator": "#56b6c2",
    "constant": "#d19a66",
    "property": "#e06c75"
  }
}
```

**Color Keys:**
- `comment`: Comments in code
- `string`: String literals
- `number`: Numeric literals
- `keyword`: Language keywords (if, for, def, etc.)
- `function`: Function names and calls
- `type`: Type names and annotations
- `variable`: Variable names
- `operator`: Operators (+, -, =, etc.)
- `constant`: Constants and literals
- `property`: Object properties and attributes

All colors should be specified as hex values (e.g., `#ff0000` for red). The system automatically converts hex colors to appropriate ANSI codes for terminal output and uses them directly for HTML output.

### Example Custom Themes

The project includes example custom themes:
- **Ocean**: Blue and teal inspired theme
- **Forest**: Earth-toned theme with greens and browns

## Development

### Building from Source

Requirements:
- Rust toolchain (1.70+)
- Python 3.8+ (for Python bindings)

#### Building the CLI Tool

```bash
# Clone the repository
git clone https://github.com/watermarkhu/tscolor.git
cd tscolor

# Build CLI binary with all language features
cargo build --release --features all-languages

# The binary will be available at target/release/tscolor
```

#### Building Python Package

Requirements:
- maturin

```bash
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