# Contributing to tscolor

Thank you for your interest in contributing to tscolor! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Rust 1.70 or later
- Python 3.8 or later
- maturin (`pip install maturin`)

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/watermarkhu/tscolor.git
   cd tscolor
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install maturin pytest
   ```

4. Build and install the package in development mode:
   ```bash
   maturin develop --features all-languages
   ```

## Project Structure

```
tscolor/
├── src/                    # Rust source code
│   ├── lib.rs             # Python bindings and module definition
│   ├── highlighter.rs     # Core syntax highlighting logic
│   ├── theme.rs           # Theme definitions
│   └── languages.rs       # Language configurations
├── tests/                 # Python tests
├── Cargo.toml             # Rust dependencies and features
├── pyproject.toml         # Python package configuration
├── example.py             # Usage examples
└── README.md              # Documentation
```

## Making Changes

### Rust Code

1. Make your changes to the Rust code in the `src/` directory
2. Check your code with:
   ```bash
   cargo check --features all-languages
   cargo clippy --features all-languages
   ```

3. Format your code:
   ```bash
   cargo fmt
   ```

### Python Bindings

When adding new functions to expose to Python:

1. Add the Rust function with `#[pyfunction]` attribute
2. Register it in the `tscolor` module function
3. Document it with docstrings
4. Add tests in `tests/`

### Adding a New Language

To add support for a new programming language:

1. Add the tree-sitter grammar dependency to `Cargo.toml`:
   ```toml
   tree-sitter-mylang = { version = "x.y.z", optional = true }
   ```

2. Add a feature for the language:
   ```toml
   [features]
   mylang = ["tree-sitter-mylang"]
   ```

3. Add language registration in `src/languages.rs`:
   ```rust
   #[cfg(feature = "mylang")]
   fn register_mylang(highlighter: &mut Highlighter) -> Result<(), String> {
       let language = tree_sitter_mylang::LANGUAGE;
       let highlights = tree_sitter_mylang::HIGHLIGHTS_QUERY;
       highlighter.register_language(
           "mylang",
           language.into(),
           highlights,
           "",
           "",
       )
   }
   ```

4. Add the language to `available_languages()` function
5. Update README.md to document the new language
6. Add tests for the new language

### Adding a New Theme

To add a new theme:

1. Edit `src/theme.rs`
2. Create a new theme function similar to `Theme::dark()` or `Theme::light()`
3. Add it to the `get_theme()` function
4. Update the `get_available_themes()` function in `src/lib.rs`
5. Add tests for the new theme

## Testing

Run the test suite:

```bash
# Run Python tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tscolor --cov-report=html
```

## Building

Build wheels for distribution:

```bash
# Build with all languages
maturin build --release --features all-languages

# Build with specific features
maturin build --release --features python
```

Use the provided script to build all feature combinations:

```bash
./build_wheels.sh
```

## Code Style

- **Rust**: Follow Rust standard style (use `cargo fmt`)
- **Python**: Follow PEP 8 style guidelines
- Write clear, descriptive commit messages
- Add docstrings to all public functions

## Pull Request Process

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/my-feature`)
3. Make your changes and commit them
4. Run tests and ensure they pass
5. Push to your fork and submit a pull request
6. Wait for review and address any feedback

## Questions?

If you have questions or need help, feel free to:
- Open an issue on GitHub
- Start a discussion in the repository

Thank you for contributing to tscolor!
