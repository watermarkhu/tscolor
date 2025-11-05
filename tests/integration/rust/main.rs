use anyhow::{Context, Result};
use std::env;
use std::fs;
use std::io::{self, Read};
use tree_sitter_highlight::{HighlightConfiguration, HighlightEvent, Highlighter};

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("Usage: {} <language> [--file <path>]", args[0]);
        eprintln!("  Reads source code from stdin and outputs highlight events");
        std::process::exit(1);
    }

    let language_name = &args[1];

    // Read source code from stdin or file
    let source = if args.len() > 3 && args[2] == "--file" {
        fs::read(&args[3])
            .with_context(|| format!("Failed to read file: {}", args[3]))?
    } else {
        let mut buffer = Vec::new();
        io::stdin()
            .read_to_end(&mut buffer)
            .context("Failed to read from stdin")?;
        buffer
    };

    // Get the language configuration
    let mut config = match language_name.as_str() {
        "python" => {
            let highlights_query = include_str!("../../../tscolor/languages/python/highlights.scm");
            HighlightConfiguration::new(
                tree_sitter_python::LANGUAGE.into(),
                "python",
                highlights_query,
                "",  // injections
                "",  // locals
            )?
        }
        "javascript" => {
            let highlights_query = include_str!("../../../tscolor/languages/javascript/highlights.scm");
            HighlightConfiguration::new(
                tree_sitter_javascript::LANGUAGE.into(),
                "javascript",
                highlights_query,
                "",  // injections
                "",  // locals
            )?
        }
        _ => {
            anyhow::bail!("Unsupported language: {}", language_name);
        }
    };

    // Configure the highlight names
    let highlight_names = &[
        "attribute",
        "comment",
        "constant",
        "constant.builtin",
        "constructor",
        "embedded",
        "error",
        "escape",
        "function",
        "function.builtin",
        "keyword",
        "number",
        "operator",
        "property",
        "punctuation",
        "punctuation.bracket",
        "punctuation.delimiter",
        "punctuation.special",
        "string",
        "string.special",
        "tag",
        "type",
        "type.builtin",
        "variable",
        "variable.builtin",
        "variable.parameter",
    ];
    config.configure(highlight_names);

    // Run the highlighter
    let mut highlighter = Highlighter::new();
    let highlights = highlighter
        .highlight(&config, &source, None, |_| None)
        .context("Failed to highlight source code")?;

    // Output events in a parseable format
    // Format: <event_type>:<byte_offset>:<highlight_index>
    // Event types: S (Source), HS (HighlightStart), HE (HighlightEnd)
    for event in highlights {
        match event? {
            HighlightEvent::Source { start, end } => {
                println!("S:{}:{}", start, end);
            }
            HighlightEvent::HighlightStart(idx) => {
                println!("HS:{}", idx.0);
            }
            HighlightEvent::HighlightEnd => {
                println!("HE");
            }
        }
    }

    Ok(())
}
