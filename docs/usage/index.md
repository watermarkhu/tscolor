# Usage Guide

Learn how to use TSColor for syntax highlighting in your projects.

## Overview

TSColor provides two main interfaces:

1. **Command Line Interface (CLI)** - For quick highlighting tasks
2. **Python API** - For programmatic highlighting in your applications

## Command Line Interface

The CLI is the quickest way to highlight files:

```bash
# Basic usage
tscolor script.py

# With options
tscolor --theme monokai --output output.html script.py
```

See [CLI Reference](cli.md) for detailed documentation.

## Python API

The Python API provides full control over the highlighting process:

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
```

## Core Concepts

### Highlighter

The `Highlighter` class is responsible for parsing code and generating highlight events:

```python
from tscolor import Highlighter

highlighter = Highlighter()
events = highlighter.highlight(config, source)
```

### Configuration

Language configurations contain tree-sitter queries for highlighting:

```python
from tscolor.languages import get_configuration

config = get_configuration("python")
```

### Themes

Themes define colors for different syntax elements:

```python
from tscolor import get_theme, list_themes

# Get a theme
theme = get_theme("dracula")

# List available themes
themes = list_themes()
```

### Formatters

Formatters convert highlight events to output formats:

```python
from tscolor.formatters import AnsiFormatter, HtmlFormatter

# ANSI formatter for terminal
ansi = AnsiFormatter(theme)
colored = ansi.format(source, events, config)

# HTML formatter
html_formatter = HtmlFormatter(theme)
html = html_formatter.format_complete(source, events, config)
```

## Topics

- [CLI Reference](cli.md) - Command-line usage
- [Themes](themes.md) - Working with themes
- [Formatters](formatters.md) - Output formatting
- [Languages](languages.md) - Language support
