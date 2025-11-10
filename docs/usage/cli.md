# CLI Reference

The TSColor command-line interface provides a simple way to highlight source code files.

## Basic Usage


```bash
tscolor [OPTIONS] [FILE]
```
## Examples

### Highlight a File

Highlight a Python file with the default Dracula theme:

```bash
tscolor script.py
```

### Choose a Theme

Use the Monokai theme:

```bash
tscolor --theme monokai script.py
```

Use GitHub Light theme:

```bash
tscolor --theme github-light script.py
```

### Export to HTML

Save highlighted code as HTML:

```bash
tscolor --output highlighted.html script.py
```

With a specific theme:

```bash
tscolor --theme monokai --output highlighted.html script.py
```

### Specify Language

For files without standard extensions, specify the language explicitly:

```bash
tscolor --language python myfile.txt
```

### Include Background Color

Include the theme's background color in terminal output:

```bash
tscolor --background script.py
```

### List Themes

Show all available themes:

```bash
tscolor --list-themes
```

Output:
```
Available themes:

Dark themes:
  • dracula by Dracula Theme
  • monokai by Wimer Hazenberg

Light themes:
  • github-light by GitHub
```

## Options

### `-l, --language TEXT`

Specify the programming language explicitly. Useful for files without standard extensions.

**Supported languages:**
- python
- javascript, jsx
- typescript, tsx
- rust
- go
- c, cpp
- java
- ruby
- php
- swift
- kotlin
- scala
- html
- css
- json
- yaml
- bash
- matlab

**Example:**
```bash
tscolor --language python file.txt
```

### `-t, --theme TEXT`

Select a color theme. Default is `dracula`.

**Available themes:**
- dracula (dark)
- monokai (dark)
- github-light (light)

**Example:**
```bash
tscolor --theme monokai script.py
```

### `-o, --output PATH`

Save output as HTML file instead of printing to terminal.

**Example:**
```bash
tscolor --output output.html script.py
```

### `-b, --background`

Include background color in terminal output.

**Example:**
```bash
tscolor --background script.py
```

### `--list-themes`

List all available themes and exit.

**Example:**
```bash
tscolor --list-themes
```

### `--version`

Show version and exit.

**Example:**
```bash
tscolor --version
```

### `-h, --help`

Show help message and exit.

**Example:**
```bash
tscolor --help
```

## Exit Codes

- `0` - Success
- `1` - Error (e.g., file not found, invalid theme, missing language parser)
- `2` - Invalid command-line arguments

## Environment

### Terminal Color Support

TSColor uses 24-bit RGB ANSI colors. For best results, use a terminal that supports true color:

- Modern terminals (iTerm2, Alacritty, Windows Terminal, GNOME Terminal, etc.)
- VS Code integrated terminal
- tmux with `set -g default-terminal "screen-256color"`

### Output Redirection

When output is redirected to a file or pipe, ANSI codes are preserved:

```bash
# Redirect to file
tscolor script.py > output.txt

# Pipe to less with color support
tscolor script.py | less -R
```

## Troubleshooting

### Language Parser Not Found

If you get an error like:

```
Error: Could not load parser for language: python
```

Install the required tree-sitter language parser:

```bash
pip install tree-sitter-python
```

### Unknown File Extension

For files with non-standard extensions:

```
Error: Could not detect language for .xyz
```

Use the `--language` option:

```bash
tscolor --language python myfile.xyz
```

### Theme Not Found

If you get:

```
Error: Theme 'mytheme' not found
```

List available themes:

```bash
tscolor --list-themes
```

And choose one of the listed themes.
