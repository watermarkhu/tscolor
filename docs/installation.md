# Installation

## Requirements

- Python 3.10 or higher
- tree-sitter >= 0.20.0

## Basic Installation

Install TSColor using pip:

```bash
pip install tscolor
```

This installs the core library with support for themes and the CLI tool.

## Installing Language Support

TSColor requires tree-sitter language parsers to be installed separately. Install the languages you need:

### Python

```bash
pip install tree-sitter-python
```

### JavaScript

```bash
pip install tree-sitter-javascript
```

### MATLAB

```bash
pip install tree-sitter-matlab
```

### Multiple Languages

Install multiple language parsers at once:

```bash
pip install tree-sitter-python tree-sitter-javascript tree-sitter-rust
```

## Installing with Extras

TSColor provides optional extras for common language groups:

### Python Support

```bash
pip install tscolor[python]
```

### JavaScript Support

```bash
pip install tscolor[javascript]
```

### MATLAB Support

```bash
pip install tscolor[matlab]
```

## Development Installation

To contribute to TSColor or run tests:

```bash
# Clone the repository
git clone https://github.com/watermarkhu/tscolor.git
cd tscolor

# Install with development dependencies using uv
uv sync --dev --all-extras

# Or with pip
pip install -e ".[dev,python,javascript,matlab]"
```

## Verifying Installation

Test that TSColor is installed correctly:

```bash
# Check version
tscolor --version

# List available themes
tscolor --list-themes

# Try highlighting a file (requires tree-sitter-python)
echo "def hello(): pass" > test.py
tscolor test.py
```

## Dependencies

### Core Dependencies

- **tree-sitter**: Core tree-sitter bindings
- **pyyaml**: YAML parsing for themes
- **click**: Command-line interface

### Development Dependencies

- **pytest**: Testing framework
- **pytest-cov**: Code coverage
- **ruff**: Linting and formatting
- **ty**: Type checking

### Documentation Dependencies

- **mkdocs**: Documentation generator
- **mkdocs-material**: Material theme for MkDocs
- **mkdocstrings**: API documentation generator
- **mkdocs-click**: CLI documentation from Click

## Troubleshooting

### No module named 'tree_sitter_python'

If you get this error when highlighting Python code:

```
Error: Could not load parser for language: python
Make sure tree-sitter-python is installed:
  pip install tree-sitter-python
```

Install the missing language parser:

```bash
pip install tree-sitter-python
```

### Import Error

If you get import errors, make sure TSColor is installed:

```bash
pip install tscolor
```

### Permission Errors

On some systems, you may need to use `--user`:

```bash
pip install --user tscolor
```

Or use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install tscolor
```
