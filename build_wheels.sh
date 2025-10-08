#!/bin/bash
# Build wheels for different feature combinations

set -e

echo "Building tscolor wheels with different feature combinations..."
echo ""

# Build base package (no languages)
echo "1. Building base package (no language features)..."
maturin build --release --out dist/

# Build with Python support
echo "2. Building with Python support..."
maturin build --release --features python --out dist/

# Build with Rust support  
echo "3. Building with Rust support..."
maturin build --release --features rust --out dist/

# Build with JavaScript support
echo "4. Building with JavaScript support..."
maturin build --release --features javascript --out dist/

# Build with JSON support
echo "5. Building with JSON support..."
maturin build --release --features json --out dist/

# Build with all languages
echo "6. Building with all languages..."
maturin build --release --features all-languages --out dist/

echo ""
echo "✅ All wheels built successfully!"
echo "Wheels are in the dist/ directory:"
ls -lh dist/*.whl
