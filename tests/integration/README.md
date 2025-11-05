# Integration Tests

This directory contains integration tests that verify tscolor's output against the official Rust tree-sitter-highlight library.

## Building the Test Helper

The integration tests use a Rust helper binary that calls tree-sitter-highlight with the same query files used by tscolor. To build this binary:

```bash
cargo build --release
```

This will create the `ts-highlight` binary in `target/release/`.

## Running the Tests

Once the binary is built, run the integration tests:

```bash
uv run pytest tests/integration/
```

If the Rust binary is not available, the tests will be skipped.

## How It Works

1. **tree-sitter.json files**: Each language in `tscolor/languages/<lang>/` has a `tree-sitter.json` file that follows the [tree-sitter configuration format](https://tree-sitter.github.io/tree-sitter/syntax-highlighting#language-detection).

2. **Rust test helper**: The `rust/main.rs` file implements a small CLI that:
   - Loads the same `highlights.scm` query files that tscolor uses
   - Runs tree-sitter-highlight on the input source code
   - Outputs highlight events in a parseable format

3. **Python integration tests**: The `test_against_rust.py` file:
   - Runs both tscolor and the Rust helper on the same source code
   - Compares the highlight events from both implementations
   - Fails if there are any differences

This ensures that tscolor's pure Python implementation produces identical results to the official Rust library.

## Adding Tests for New Languages

To add integration tests for a new language:

1. Add the language to `Cargo.toml` dependencies (e.g., `tree-sitter-ruby = "0.x"`)
2. Add a match arm in `rust/main.rs` for the language
3. Add a test class in `test_against_rust.py` (e.g., `TestRubyAgainstRust`)
4. Create language configuration in `tscolor/languages/<lang>/tree-sitter.json`
