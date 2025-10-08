#!/bin/bash

# Build script for tscolor
# This script builds the tscolor binary with all language features

set -e

echo "Building tscolor with all language features..."

# Build in release mode for better performance
cargo build --release --features all-languages

echo "Build completed successfully!"
echo "Binary location: target/release/tscolor"
echo ""
echo "To install globally, run:"
echo "  sudo cp target/release/tscolor /usr/local/bin/"
echo ""
echo "To test locally, run:"
echo "  ./target/release/tscolor <file> <language> [--html <output.html>] [--theme <dark|light>]"