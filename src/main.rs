use std::fs;
use std::io::{self, Write};
use std::process;

mod cli;
mod theme;
mod highlighter;
mod languages;
mod language_detection;

use cli::Args;
use theme::{load_theme, get_available_themes};
use highlighter::{Highlighter, format_terminal, format_html};
use languages::{init_languages, available_languages};

fn main() {
    let args = Args::parse_args();

    // Get the language (auto-detect if not provided)
    let language = match args.get_language() {
        Ok(lang) => {
            // Print auto-detection message if language was not explicitly provided
            if args.language.is_none() {
                eprintln!("Auto-detected language: {}", lang);
            }
            lang
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            process::exit(1);
        }
    };

    // Read the input file
    let code = match fs::read_to_string(&args.file) {
        Ok(content) => content,
        Err(e) => {
            eprintln!("Error reading file '{}': {}", args.file.display(), e);
            process::exit(1);
        }
    };

    // Create highlighter and initialize languages
    let mut highlighter = Highlighter::new();
    if let Err(e) = init_languages(&mut highlighter) {
        eprintln!("Error initializing languages: {}", e);
        process::exit(1);
    }

    // Check if the requested language is available
    let available_langs = available_languages();
    if !available_langs.contains(&language) {
        eprintln!(
            "Language '{}' is not available. Available languages: {}",
            language,
            available_langs.join(", ")
        );
        process::exit(1);
    }

    // Check if the requested theme is available
    let available_themes = get_available_themes();
    if !available_themes.contains(&args.theme) {
        eprintln!(
            "Theme '{}' is not available. Available themes: {}",
            args.theme,
            available_themes.join(", ")
        );
        process::exit(1);
    }

    // Get highlight events
    let events = match highlighter.highlight(&language, &code) {
        Ok(events) => events,
        Err(e) => {
            eprintln!("Error highlighting code: {}", e);
            process::exit(1);
        }
    };

    // Get theme
    let theme = load_theme(&args.theme);

    // Format output based on requested format
    let result = match args.output_format() {
        "html" => format_html(&code, &events, &theme),
        _ => format_terminal(&code, &events, &theme),
    };

    // Output the result
    if let Some(html_path) = &args.html {
        // Write HTML to file
        match fs::write(html_path, &result) {
            Ok(_) => {
                println!("HTML output written to: {}", html_path.display());
            }
            Err(e) => {
                eprintln!("Error writing HTML file '{}': {}", html_path.display(), e);
                process::exit(1);
            }
        }
    } else {
        // Print to terminal
        print!("{}", result);
        // Ensure output is flushed
        io::stdout().flush().unwrap_or_else(|e| {
            eprintln!("Error flushing output: {}", e);
            process::exit(1);
        });
    }
}