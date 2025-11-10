# API Reference

Complete API documentation for TSColor.

## Core Components

### Highlighter

The main highlighter class for processing source code:

- [Highlighter API](highlighter.md)

### Configuration

Language configuration and query management:

- [Configuration API](configuration.md)

### Theme

Theme loading and management:

- [Theme API](theme.md)

### Formatters

Output formatting:

- [ANSI Formatter](formatters/ansi.md)
- [HTML Formatter](formatters/html.md)

### Events

Highlight event types:

- [Events API](events.md)

### Scope

Local scope tracking:

- [Scope API](scope.md)

## Quick Reference

### Main Classes

| Class | Module | Description |
|-------|--------|-------------|
| `Highlighter` | `tscolor` | Main highlighter class |
| `HighlightConfiguration` | `tscolor.configuration` | Language configuration |
| `Theme` | `tscolor.theme` | Theme definition |
| `AnsiFormatter` | `tscolor.formatters` | ANSI terminal formatter |
| `HtmlFormatter` | `tscolor.formatters` | HTML formatter |

### Main Functions

| Function | Module | Description |
|----------|--------|-------------|
| `get_theme()` | `tscolor` | Get a theme by name |
| `list_themes()` | `tscolor` | List available themes |
| `get_configuration()` | `tscolor.languages` | Get language configuration |
| `register_language()` | `tscolor.languages` | Register a language |

## Import Shortcuts

TSColor provides convenient imports from the main package:

```python
from tscolor import (
    Highlighter,
    get_theme,
    list_themes,
    get_theme_info,
    register_theme,
    __version__,
)
```

## Type Hints

TSColor is fully typed and works with type checkers like mypy and pyright.

```python
from tscolor import Highlighter, get_theme
from tscolor.languages import get_configuration
from tscolor.formatters import AnsiFormatter
from typing import Iterable

config = get_configuration("python")
theme = get_theme("dracula")
highlighter = Highlighter()

source: bytes = b"def hello(): pass"
events: Iterable = highlighter.highlight(config, source)

formatter: AnsiFormatter = AnsiFormatter(theme)
output: str = formatter.format(source, events, config)
```
