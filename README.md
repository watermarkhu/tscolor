# TSColor

A pure Python implementation of tree-sitter-highlight for syntax highlighting using tree-sitter parsers.

## Features

- 🎨 **Multiple Themes**: Built-in Dracula theme, easily extensible
- 🌍 **Multi-Language**: Support for any language with tree-sitter grammar
- 🔗 **Language Injection**: Support for embedded languages (e.g., JavaScript in HTML)
- 🔍 **Local Scope Tracking**: Track local variable definitions and references
- 🖥️ **Terminal Output**: ANSI color formatting for beautiful terminal output
- 🌐 **HTML Output**: Generate syntax-highlighted HTML for web pages
- 🔌 **Extensible**: Easy to add new languages and themes

## Architecture

TSColor closely follows the architecture of the Rust tree-sitter-highlight library:

### Core Components

1. **Highlighter**: Main class coordinating the highlighting process with multi-layer support
2. **HighlightConfiguration**: Holds language-specific queries (highlights, injections, locals)
3. **HighlightLayer**: Represents a single language layer (base or injected)
4. **Events**: Stream of events (SourceEvent, HighlightStartEvent, HighlightEndEvent)
5. **Formatters**: Convert events to output formats (ANSI, HTML)
6. **Themes**: Define color schemes for syntax elements
7. **Scope Tracking**: Local variable definition and reference resolution

### Key Features from Rust Implementation

- **Multi-layer processing**: Proper handling of language injection
- **Combined queries**: Injections + locals + highlights in a single query
- **Local scope tracking**: Variable definitions and references
- **Overlap handling**: Deduplication of highlights across layers
- **Event prioritization**: Proper ordering by position, type, and depth

## Installation

```bash
pip install tscolor
```

You'll also need to install tree-sitter language bindings:

```bash
pip install tree-sitter-python
pip install tree-sitter-javascript
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
source = b\"\"\"
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
\"\"\"

events = highlighter.highlight(config, source)

# Format for terminal output
formatter = AnsiFormatter(theme)
colored_code = formatter.format(source, events, config)
print(colored_code)
```

## Examples

See the `examples/` directory for more examples:

```bash
python examples/simple_highlight.py
python examples/html_export.py
python examples/javascript_example.py
```

## Documentation

For full documentation, see the inline documentation and examples.

## License

MIT License

## Credits

- Inspired by [tree-sitter-highlight](https://github.com/tree-sitter/tree-sitter/tree/master/crates/highlight)
- Built on [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter)
- Dracula theme from [draculatheme.com](https://draculatheme.com/)
