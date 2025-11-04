# Contributing to TSColor

Thank you for your interest in contributing to TSColor! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Setting Up Your Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/watermarkhu/tscolor.git
   cd tscolor
   ```

2. Install dependencies with uv:
   ```bash
   uv sync --dev --all-extras
   ```

   This installs all development dependencies including:
   - pytest for testing
   - ruff for linting and formatting
   - ty for type checking
   - mkdocs for documentation

## Development Workflow

### Running Tests

Run the test suite with pytest:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=tscolor --cov-report=term-missing
```

### Code Quality

Before committing, ensure your code passes all checks:

#### Linting

```bash
uv run ruff check --fix
```

#### Formatting

```bash
uv run ruff format
```

#### Type Checking

```bash
uv run ty check
```

### Running All Checks

Run all quality checks at once:

```bash
uv run ruff check --fix && uv run ruff format && uv run ty check && uv run pytest
```

## Code Style

TSColor follows these guidelines:

- **PEP 8** style guide (enforced by ruff)
- **Type hints** for all public APIs
- **Google-style docstrings** for documentation
- **100 character** line length

### Example Docstring

```python
def highlight(
    self,
    config: HighlightConfiguration,
    source: bytes,
    should_cancel: Optional[Callable[[], bool]] = None,
) -> Iterator[HighlightEvent]:
    """Highlight source code using tree-sitter.

    Args:
        config: Language configuration with queries
        source: Source code as bytes
        should_cancel: Optional callback to check for cancellation

    Returns:
        Iterator of highlight events

    Raises:
        ValueError: If configuration is invalid
    """
    pass
```

## Making Changes

### Branching Strategy

- Create a feature branch from `main`: `git checkout -b feature/your-feature`
- Make your changes
- Ensure all tests pass
- Create a pull request

### Commit Messages

Write clear, concise commit messages:

```
Add support for Rust language highlighting

- Add Rust query files
- Register Rust in language map
- Add tests for Rust highlighting
```

## Adding New Features

### Adding a New Language

1. Install the tree-sitter parser:
   ```bash
   pip install tree-sitter-{language}
   ```

2. Create query files in `tscolor/languages/{language}/`:
   - `highlights.scm` (required)
   - `injections.scm` (optional)
   - `locals.scm` (optional)

3. Add tests in `tests/test_highlighter.py`

4. Update documentation in `docs/usage/languages.md`

### Adding a New Theme

1. Create a YAML file in `tscolor/themes/`:
   ```yaml
   name: my-theme
   category: dark
   author: Your Name
   
   colors:
     foreground: "#ffffff"
     background: "#000000"
     keyword: "#ff6188"
     # ... more colors
   ```

2. Add tests in `tests/test_theme.py`

3. Update documentation in `docs/usage/themes.md`

### Adding a New Formatter

1. Create a new formatter class in `tscolor/formatters/`

2. Implement the formatter interface:
   ```python
   def format(
       self,
       source: bytes,
       events: Iterable[HighlightEvent],
       config: HighlightConfiguration,
   ) -> str:
       """Format highlighted code."""
       pass
   ```

3. Add tests in `tests/test_formatters.py`

4. Update documentation in `docs/usage/formatters.md`

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_highlight_python_code`
- Group related tests in classes
- Use fixtures for common setup

### Test Structure

```python
import pytest
from tscolor import Highlighter

class TestHighlighting:
    """Test basic highlighting functionality."""

    @pytest.fixture
    def highlighter(self):
        """Fixture providing a highlighter instance."""
        return Highlighter()

    def test_highlight_simple_code(self, highlighter):
        """Test highlighting simple Python code."""
        # Test implementation
        pass
```

### Running Specific Tests

```bash
# Run a specific file
uv run pytest tests/test_highlighter.py

# Run a specific test
uv run pytest tests/test_highlighter.py::TestBasicHighlighting::test_highlight_simple_code

# Run tests matching a pattern
uv run pytest -k "highlight"
```

## Documentation

### Building Documentation

Build the documentation locally:

```bash
uv sync --group docs
uv run mkdocs serve
```

Then visit http://127.0.0.1:8000/ to view the docs.

### Writing Documentation

- Update relevant `.md` files in the `docs/` directory
- Use clear, concise language
- Include code examples
- Follow the existing structure

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Document** your changes
6. **Submit** a pull request

### Pull Request Checklist

- [ ] All tests pass
- [ ] Code is properly formatted (ruff format)
- [ ] Code passes linting (ruff check)
- [ ] Type checking passes (ty check)
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if applicable)
- [ ] Commit messages are clear

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/watermarkhu/tscolor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/watermarkhu/tscolor/discussions)

## Code of Conduct

Be respectful and constructive in all interactions. We're all here to make TSColor better!

## License

By contributing to TSColor, you agree that your contributions will be licensed under the MIT License.
