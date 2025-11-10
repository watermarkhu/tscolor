# TSColor

Pure Python implementation of tree-sitter-highlight for syntax highlighting.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- 🎨 **Multiple themes** - Built-in Dracula, Monokai, and GitHub Light themes
- 🔤 **Multiple languages** - Python, JavaScript, MATLAB, and more
- 📤 **Multiple outputs** - ANSI terminal colors and HTML
- 🔧 **Extensible** - Add custom themes and languages

## Quick Start

### Installation

```bash
pip install tscolor tree-sitter-python
```

### Command Line

```bash
# Highlight a file
tscolor script.py

# Use a different theme
tscolor --theme monokai script.py

# Export to HTML
tscolor --output highlighted.html script.py

# List themes
tscolor --list-themes
```

### Python API

```python
from tscolor import Highlighter, get_theme
from tscolor.languages import get_configuration
from tscolor.formatters import AnsiFormatter

# Setup
config = get_configuration("python")
theme = get_theme("dracula")
highlighter = Highlighter()

# Highlight
source = b"def hello(): pass"
events = highlighter.highlight(config, source)

# Format
formatter = AnsiFormatter(theme)
output = formatter.format(source, events, config)
print(output)
```

## Documentation

For full documentation, visit: **[TSColor Documentation](https://watermarkhu.github.io/tscolor)**

- [Installation Guide](https://watermarkhu.github.io/tscolor/installation/)
- [Quick Start](https://watermarkhu.github.io/tscolor/quickstart/)
- [Usage Guide](https://watermarkhu.github.io/tscolor/usage/)
- [API Reference](https://watermarkhu.github.io/tscolor/api/)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by [tree-sitter-highlight](https://github.com/tree-sitter/tree-sitter/tree/master/crates/highlight) (Rust)
- Powered by [tree-sitter](https://tree-sitter.github.io/tree-sitter/)
