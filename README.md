# TSColor

A pure Python implementation of tree-sitter-highlight for syntax highlighting using tree-sitter parsers.

## Features

- 🎨 **Multiple Themes**: YAML-based theme system with Dracula, GitHub Light, and Monokai
- 🌓 **Light/Dark Themes**: Themes categorized as light or dark for easy selection
- 🌍 **Multi-Language**: Support for any language with tree-sitter grammar
- 🔗 **Language Injection**: Support for embedded languages (e.g., JavaScript in HTML)
- 🔍 **Local Scope Tracking**: Track local variable definitions and references
- 🖥️ **Terminal Output**: ANSI color formatting for beautiful terminal output
- 🌐 **HTML Output**: Generate syntax-highlighted HTML for web pages
- 🔌 **Extensible**: Easy to add new languages and themes
- ✅ **Well Tested**: Comprehensive pytest test suite

## Installation

```bash
pip install tscolor
```

You'll also need to install tree-sitter language bindings:

```bash
pip install tree-sitter-python tree-sitter-javascript
```

## Quick Start

```python
from tscolor import Highlighter, get_theme
from tscolor.languages import register_language, get_configuration
from tscolor.formatters import AnsiFormatter
import tree_sitter_python as ts_python

# Register the Python language
register_language("python", ts_python.language())

# Set up highlighter and theme
highlighter = Highlighter()
config = get_configuration("python")
theme = get_theme("dracula")

# Highlight some code
source = b"""
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

events = highlighter.highlight(config, source)

# Format for terminal output
formatter = AnsiFormatter(theme)
colored_code = formatter.format(source, events, config)
print(colored_code)
```

## Themes

TSColor includes three built-in themes, all defined in YAML:

### Dark Themes
- **Dracula**: The popular Dracula theme with official colors
- **Monokai**: Classic Monokai color scheme

### Light Themes
- **GitHub Light**: GitHub's light color scheme

### Working with Themes

```python
from tscolor import get_theme, list_themes, get_theme_info

# List all available themes
themes = list_themes()
print(themes)  # ['dracula', 'github-light', 'monokai']

# List only dark themes
dark_themes = list_themes(category='dark')
print(dark_themes)  # ['dracula', 'monokai']

# List only light themes
light_themes = list_themes(category='light')
print(light_themes)  # ['github-light']

# Get theme information
info = get_theme_info('dracula')
print(info['category'])  # 'dark'
print(info['author'])    # 'Dracula Theme'

# Check if theme is light or dark
theme = get_theme('dracula')
print(theme.is_dark())   # True
print(theme.is_light())  # False
```

### Creating Custom Themes

Create a YAML file in the `themes/` directory:

```yaml
name: My Custom Theme
category: dark  # or "light"
author: Your Name
description: A custom color scheme
url: https://example.com

background: "#1e1e1e"
foreground: "#d4d4d4"
selection: "#264f78"
comment: "#6a9955"

colors:
  keyword: "#569cd6"
  function: "#dcdcaa"
  string: "#ce9178"
  comment: "#6a9955"
  type: "#4ec9b0"
  variable: "#9cdcfe"
  # ... more mappings
```

Then register and use it:

```python
from pathlib import Path
from tscolor import Theme, register_theme, get_theme

# Load from YAML
theme = Theme.from_yaml(Path("my-theme.yaml"))
register_theme(theme)

# Use it
theme = get_theme("my custom theme")
```

## HTML Export

```python
from tscolor.formatters import HtmlFormatter

html_formatter = HtmlFormatter(theme)

# Generate highlighted HTML
events = highlighter.highlight(config, source)
html = html_formatter.format_complete(
    source,
    events,
    config,
    title="My Python Code"
)

# Save to file
with open("highlighted.html", "w") as f:
    f.write(html)
```

## Project Structure

```
tscolor/
├── tscolor/              # Main package
│   ├── __init__.py
│   ├── highlighter.py   # Core highlighter with multi-layer support
│   ├── configuration.py # Query configuration
│   ├── theme.py         # Theme system
│   ├── events.py        # Event types
│   ├── scope.py         # Local scope tracking
│   ├── layer.py         # Layer management
│   ├── formatters/      # Output formatters
│   │   ├── ansi.py
│   │   └── html.py
│   └── languages/       # Language query files
│       ├── python/
│       │   └── highlights.scm
│       └── javascript/
│           └── highlights.scm
├── themes/              # YAML theme definitions
│   ├── dracula.yaml
│   ├── github-light.yaml
│   └── monokai.yaml
├── tests/               # Pytest test suite
│   ├── test_theme.py
│   ├── test_highlighter.py
│   ├── test_formatters.py
│   └── test_scope.py
└── examples/            # Usage examples
    ├── simple_highlight.py
    ├── html_export.py
    └── javascript_example.py
```

## Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=tscolor --cov-report=html
```

## Examples

See the `examples/` directory for complete examples:

```bash
python examples/simple_highlight.py
python examples/html_export.py
python examples/javascript_example.py
```

## Adding New Languages

1. **Install the tree-sitter language binding:**
   ```bash
   pip install tree-sitter-rust
   ```

2. **Create a directory with query files:**
   ```
   tscolor/languages/rust/
   ├── highlights.scm   (required)
   ├── injections.scm   (optional)
   └── locals.scm       (optional)
   ```

3. **Register the language:**
   ```python
   import tree_sitter_rust as ts_rust
   from tscolor.languages import register_language

   register_language("rust", ts_rust.language())
   ```

Query files can be found in official tree-sitter repositories:
- [tree-sitter-python](https://github.com/tree-sitter/tree-sitter-python/tree/master/queries)
- [tree-sitter-javascript](https://github.com/tree-sitter/tree-sitter-javascript/tree/master/queries)
- [More languages](https://github.com/tree-sitter)

## Architecture

TSColor closely follows the Rust tree-sitter-highlight architecture:

- **Highlighter**: Multi-layer highlighting with language injection support
- **HighlightConfiguration**: Combined query system (injections + locals + highlights)
- **HighlightLayer**: Per-language layer with scope tracking
- **ScopeStack**: Local variable definition/reference resolution
- **Events**: Streaming event generation (SourceEvent, HighlightStartEvent, HighlightEndEvent)
- **Formatters**: ANSI and HTML output generation
- **Theme System**: YAML-based themes with light/dark categorization

## License

MIT License

## Credits

- Inspired by [tree-sitter-highlight](https://github.com/tree-sitter/tree-sitter/tree/master/crates/highlight)
- Built on [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter)
- Dracula theme from [draculatheme.com](https://draculatheme.com/)
- GitHub theme from [github.com](https://github.com)
- Monokai theme from [monokai.pro](https://monokai.pro)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
