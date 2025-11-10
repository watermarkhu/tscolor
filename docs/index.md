# TSColor

Pure Python implementation of tree-sitter-highlight for syntax highlighting.

## Overview

TSColor is a Python library that provides syntax highlighting for source code using [tree-sitter](https://tree-sitter.github.io/tree-sitter/) parsers. It's a pure Python implementation inspired by the Rust `tree-sitter-highlight` crate, offering:

- **Accurate syntax highlighting** powered by tree-sitter parsers
- **Multiple output formats**: ANSI terminal colors and HTML
- **Customizable themes** with YAML configuration
- **Language injection support** for embedded languages
- **Local scope tracking** for context-aware highlighting
- **Command-line interface** for quick highlighting tasks

## Features

### 🎨 Multiple Themes

Choose from built-in themes or create your own:

- **Dracula** (dark)
- **Monokai** (dark)
- **GitHub Light** (light)

Themes are defined in simple YAML files with support for:

- Full RGB color specification
- Foreground, background, and selection colors
- Theme metadata (author, description, URL)
- Light/dark categorization

### 🔤 Multiple Languages

Built-in support for popular languages:

- Python
- JavaScript/TypeScript
- MATLAB
- Rust, Go, C/C++, Java
- Ruby, PHP, Swift, Kotlin, Scala
- HTML, CSS, JSON, YAML
- And more!

### 📤 Multiple Output Formats

- **ANSI Terminal**: 24-bit RGB colors for modern terminals
- **HTML**: Inline styles or CSS classes with complete document generation

### 🔧 Extensible

- Add custom themes via YAML
- Register additional tree-sitter languages
- Customize highlight capture names

## Quick Example

```python
from tscolor import Highlighter, get_theme
from tscolor.languages import get_configuration
from tscolor.formatters import AnsiFormatter

# Set up
config = get_configuration("python")
theme = get_theme("dracula")
highlighter = Highlighter()

# Highlight code
source = b"def hello(): pass"
events = highlighter.highlight(config, source)

# Format for terminal
formatter = AnsiFormatter(theme)
colored = formatter.format(source, events, config)
print(colored)
```

## Installation

See the [Installation](installation.md) page for detailed instructions.

## Command Line Usage

```bash
# Highlight a file
tscolor script.py

# Use a specific theme
tscolor --theme monokai script.py

# Export to HTML
tscolor --output output.html script.py

# List available themes
tscolor --list-themes
```

## Project Goals

TSColor aims to provide a pure Python alternative to tree-sitter-highlight with:

1. **Simplicity**: Easy to install and use with minimal dependencies
2. **Flexibility**: Support for multiple themes, languages, and output formats
3. **Accuracy**: Leverage tree-sitter for precise syntax understanding
4. **Performance**: Efficient highlighting for interactive use

## Links

- [GitHub Repository](https://github.com/watermarkhu/tscolor)
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/)
- [tree-sitter-highlight (Rust)](https://github.com/tree-sitter/tree-sitter/tree/master/crates/highlight)
