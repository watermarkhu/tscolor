# Formatters

Formatters convert highlight events into various output formats.

## Available Formatters

TSColor provides two built-in formatters:

1. **AnsiFormatter** - For terminal output with ANSI color codes
2. **HtmlFormatter** - For HTML output with inline styles or CSS classes

## ANSI Formatter

The ANSI formatter produces colored output for terminals using 24-bit RGB ANSI escape codes.

### Basic Usage

```python
from tscolor.formatters import AnsiFormatter

formatter = AnsiFormatter(theme)
colored = formatter.format(source, events, config)
print(colored)
```

### With Background Color

```python
colored = formatter.format_with_background(source, events, config)
print(colored)
```

### Example

```python
from tscolor import Highlighter, get_theme
from tscolor.languages import get_configuration
from tscolor.formatters import AnsiFormatter

config = get_configuration("python")
theme = get_theme("dracula")
highlighter = Highlighter()

source = b"def hello(): pass"
events = highlighter.highlight(config, source)

formatter = AnsiFormatter(theme)
colored = formatter.format(source, events, config)
print(colored)
# Output: \033[38;2;255;121;198mdef\033[0m \033[38;2;80;250;123mhello\033[0m...
```

## HTML Formatter

The HTML formatter generates HTML with syntax highlighting.

### Basic Usage

```python
from tscolor.formatters import HtmlFormatter

formatter = HtmlFormatter(theme)
html = formatter.format(source, events, config)
```

### Complete HTML Document

Generate a complete HTML page:

```python
html = formatter.format_complete(
    source,
    events,
    config,
    title="My Code",
    language_name="python"
)
```

### Using CSS Classes

Instead of inline styles, use CSS classes:

```python
formatter = HtmlFormatter(theme, use_classes=True)
html = formatter.format(source, events, config)
css = formatter.generate_css()
```

### Example

```python
from tscolor import Highlighter, get_theme
from tscolor.languages import get_configuration
from tscolor.formatters import HtmlFormatter

config = get_configuration("python")
theme = get_theme("dracula")
highlighter = Highlighter()

source = b"def hello(): pass"
events = highlighter.highlight(config, source)

# Generate HTML with inline styles
formatter = HtmlFormatter(theme)
html = formatter.format_complete(
    source,
    events,
    config,
    title="Python Example"
)

# Save to file
with open("output.html", "w") as f:
    f.write(html)
```

## Formatter Options

### AnsiFormatter Options

#### Constructor

```python
AnsiFormatter(theme: Theme)
```

**Parameters:**

- `theme` - Theme to use for colors

#### Methods

##### format

```python
format(source: bytes, events: Iterable[Event], config: HighlightConfiguration) -> str
```

Format code with ANSI colors (no background).

##### format_with_background

```python
format_with_background(source: bytes, events: Iterable[Event], config: HighlightConfiguration) -> str
```

Format code with ANSI colors and background color.

### HtmlFormatter Options

#### Constructor

```python
HtmlFormatter(theme: Theme, use_classes: bool = False)
```

**Parameters:**

- `theme` - Theme to use for colors
- `use_classes` - If True, use CSS classes instead of inline styles

#### Methods

##### format

```python
format(source: bytes, events: Iterable[Event], config: HighlightConfiguration) -> str
```

Format code as HTML (just the code, no document structure).

##### format_complete

```python
format_complete(
    source: bytes,
    events: Iterable[Event],
    config: HighlightConfiguration,
    title: str = "Highlighted Code",
    language_name: Optional[str] = None
) -> str
```

Format code as a complete HTML document.

**Parameters:**

- `source` - Source code bytes
- `events` - Highlight events
- `config` - Language configuration
- `title` - HTML document title
- `language_name` - Language name for display (optional)

##### generate_css

```python
generate_css() -> str
```

Generate CSS stylesheet for use with `use_classes=True`.

## Output Examples

### ANSI Output

ANSI output includes escape codes for terminal colors:

```
\033[38;2;255;121;198mdef\033[0m \033[38;2;80;250;123mhello\033[0m\033[38;2;248;248;242m(\033[0m\033[38;2;248;248;242m)\033[0m\033[38;2;248;248;242m:\033[0m \033[38;2;255;121;198mpass\033[0m
```

When printed to a terminal, this displays as colored text.

### HTML with Inline Styles

```html
<span style="color: #ff79c6;">def</span> <span style="color: #50fa7b;">hello</span><span style="color: #f8f8f2;">(</span><span style="color: #f8f8f2;">)</span><span style="color: #f8f8f2;">:</span> <span style="color: #ff79c6;">pass</span>
```

### HTML with CSS Classes

```html
<span class="keyword">def</span> <span class="function">hello</span><span class="punctuation">(</span><span class="punctuation">)</span><span class="punctuation">:</span> <span class="keyword">pass</span>
```

With CSS:

```css
.keyword { color: #ff79c6; }
.function { color: #50fa7b; }
.punctuation { color: #f8f8f2; }
```

### Complete HTML Document

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Example</title>
    <style>
        body {
            background-color: #282a36;
            color: #f8f8f2;
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 20px;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        code {
            font-family: 'Courier New', Courier, monospace;
        }
    </style>
</head>
<body>
    <pre><code><span style="color: #ff79c6;">def</span> <span style="color: #50fa7b;">hello</span>...
```

## Custom Formatters

You can create custom formatters by subclassing the base formatter classes or implementing the formatter interface.

### Formatter Interface

A formatter should implement:

```python
def format(
    self,
    source: bytes,
    events: Iterable[Event],
    config: HighlightConfiguration
) -> str:
    """Format highlighted code.

    Args:
        source: Source code bytes
        events: Highlight events
        config: Language configuration

    Returns:
        Formatted output string
    """
    pass
```

### Example Custom Formatter

```python
from tscolor.formatters import AnsiFormatter

class CustomFormatter(AnsiFormatter):
    def format(self, source, events, config):
        # Custom formatting logic
        result = super().format(source, events, config)
        # Add custom modifications
        return result
```

## Performance

### Memory Usage

Formatters iterate through events and build the output string incrementally. Memory usage is proportional to the output size.

### Speed

- ANSI formatting is very fast (minimal processing)
- HTML formatting is slightly slower due to escaping

### Large Files

For large files (>1MB), consider:

- Processing in chunks
- Streaming output to disk
- Using a progress indicator

## Tips

### ANSI Output

- Use `format()` for cleaner output without background
- Use `format_with_background()` when background color is important
- Test in your target terminal for color accuracy

### HTML Output

- Use `use_classes=True` for smaller output and easier theming
- Include proper `<pre><code>` tags for code blocks
- Consider syntax highlighting CSS libraries for consistency

### Both Formatters

- Reuse formatter instances for better performance
- Cache formatted output when highlighting the same code multiple times
- Choose formatter based on your use case (terminal vs web)
