# Quick Start

Get started with TSColor in minutes!

## Installation

First, install TSColor and a language parser:

```bash
pip install tscolor tree-sitter-python
```

## Command Line Usage

The quickest way to use TSColor is via the command line:

```bash
# Highlight a Python file
tscolor script.py

# Use a different theme
tscolor --theme monokai script.py

# Export to HTML
tscolor --output highlighted.html script.py

# Show all available themes
tscolor --list-themes
```

## Python API - Basic Usage

### Highlighting Code

```python
from tscolor import Highlighter, get_theme
from tscolor.languages import register_language, get_configuration
from tscolor.formatters import AnsiFormatter
import tree_sitter_python as tsp

# Register the Python language
register_language("python", tsp.language())

# Get configuration and theme
config = get_configuration("python")
theme = get_theme("dracula")

# Create highlighter
highlighter = Highlighter()

# Highlight some code
source = b"""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""

events = highlighter.highlight(config, source)

# Format for terminal
formatter = AnsiFormatter(theme)
colored = formatter.format(source, events, config)
print(colored)
```

### HTML Output

```python
from tscolor.formatters import HtmlFormatter

# ... (setup as above)

# Format as HTML
formatter = HtmlFormatter(theme)
html = formatter.format_complete(
    source,
    events,
    config,
    title="My Code"
)

# Save to file
with open("output.html", "w") as f:
    f.write(html)
```

## Working with Themes

### List Available Themes

```python
from tscolor import list_themes

# List all themes
all_themes = list_themes()
print(f"All themes: {all_themes}")

# List only dark themes
dark_themes = list_themes(category="dark")
print(f"Dark themes: {dark_themes}")

# List only light themes
light_themes = list_themes(category="light")
print(f"Light themes: {light_themes}")
```

### Get Theme Information

```python
from tscolor import get_theme_info

info = get_theme_info("dracula")
print(f"Theme: {info['name']}")
print(f"Category: {info['category']}")
print(f"Author: {info['author']}")
```

### Using Different Themes

```python
from tscolor import get_theme

# Load different themes
dracula = get_theme("dracula")
monokai = get_theme("monokai")
github_light = get_theme("github-light")

# Check if a theme is dark or light
if dracula.is_dark():
    print("Dracula is a dark theme")
```

## Supported Languages

TSColor supports any language with a tree-sitter parser. Here are some examples:

### JavaScript

```python
import tree_sitter_javascript as tsj
from tscolor.languages import register_language, get_configuration

register_language("javascript", tsj.language())
config = get_configuration("javascript")

source = b"""
function hello() {
    console.log("Hello, world!");
}
"""
```

### Multiple Languages

```python
import tree_sitter_python as tsp
import tree_sitter_javascript as tsj

from tscolor.languages import register_language

# Register multiple languages
register_language("python", tsp.language())
register_language("javascript", tsj.language())
```

## Customizing Output

### ANSI with Background Color

```python
from tscolor.formatters import AnsiFormatter

formatter = AnsiFormatter(theme)

# Include background color
colored = formatter.format_with_background(source, events, config)
print(colored)
```

### HTML with CSS Classes

```python
from tscolor.formatters import HtmlFormatter

formatter = HtmlFormatter(theme, use_classes=True)

# Generate HTML with CSS classes
html = formatter.format(source, events, config)

# Generate CSS stylesheet
css = formatter.generate_css()
```

## Next Steps

- Learn more about [CLI usage](usage/cli.md)
- Explore [themes](usage/themes.md)
- Read the [API reference](api/index.md)
- See [formatter options](usage/formatters.md)
