use clap::Parser;
use std::path::PathBuf;

use crate::language_detection;

/// A syntax highlighter using tree-sitter
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
pub struct Args {
    /// Input file path to highlight
    pub file: PathBuf,

    /// Programming language (e.g., python, rust, javascript, json). 
    /// If not provided, will be auto-detected from file extension.
    pub language: Option<String>,

    /// Output HTML to file instead of terminal
    #[arg(long)]
    pub html: Option<PathBuf>,

    /// Theme to use (dark or light)
    #[arg(long, default_value = "dark")]
    pub theme: String,
}

impl Args {
    /// Parse command line arguments
    pub fn parse_args() -> Self {
        Args::parse()
    }

    /// Get the output format based on whether HTML output is requested
    pub fn output_format(&self) -> &str {
        if self.html.is_some() {
            "html"
        } else {
            "terminal"
        }
    }
    
    /// Get the language, either from the argument or auto-detected
    pub fn get_language(&self) -> Result<String, String> {
        match &self.language {
            Some(lang) => Ok(lang.clone()),
            None => language_detection::detect_language(&self.file)
                .ok_or_else(|| {
                    format!(
                        "Could not auto-detect language for '{}'. Please specify the language explicitly.\n\
                         Supported extensions: {}",
                        self.file.display(),
                        language_detection::supported_extensions()
                    )
                }),
        }
    }
}