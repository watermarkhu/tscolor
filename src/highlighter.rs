use tree_sitter::Language;
use tree_sitter_highlight::{Highlighter as TSHighlighter, HighlightConfiguration, HighlightEvent};
use crate::theme::Theme;
use std::collections::HashMap;

pub struct Highlighter {
    ts_highlighter: TSHighlighter,
    configs: HashMap<String, HighlightConfiguration>,
}

impl Highlighter {
    pub fn new() -> Self {
        Self {
            ts_highlighter: TSHighlighter::new(),
            configs: HashMap::new(),
        }
    }

    /// Register a language with its tree-sitter configuration
    pub fn register_language(
        &mut self,
        language_name: &str,
        language: Language,
        highlights_query: &str,
        injections_query: &str,
        locals_query: &str,
    ) -> Result<(), String> {
        let mut config = HighlightConfiguration::new(
            language,
            language_name,
            highlights_query,
            injections_query,
            locals_query,
        ).map_err(|e| format!("Failed to create highlight configuration: {:?}", e))?;

        // Configure highlight names
        config.configure(&[
            "comment",
            "string",
            "number",
            "keyword",
            "function",
            "type",
            "variable",
            "operator",
            "constant",
            "property",
        ]);

        self.configs.insert(language_name.to_string(), config);
        Ok(())
    }

    /// Get highlight events for a piece of code
    pub fn highlight(
        &mut self,
        language_name: &str,
        source_code: &str,
    ) -> Result<Vec<HighlightEvent>, String> {
        let config = self.configs.get(language_name)
            .ok_or_else(|| format!("Language '{}' not registered", language_name))?;

        let highlights = self.ts_highlighter
            .highlight(config, source_code.as_bytes(), None, |_| None)
            .map_err(|e| format!("Highlighting failed: {:?}", e))?;

        let events: Result<Vec<_>, _> = highlights.collect();
        events.map_err(|e| format!("Error collecting highlights: {:?}", e))
    }
}

/// Format highlighted code as ANSI-colored terminal output
pub fn format_terminal(
    source_code: &str,
    events: &[HighlightEvent],
    theme: &Theme,
) -> String {
    let mut result = String::new();
    let mut current_pos = 0;
    let bytes = source_code.as_bytes();
    let highlight_names = [
        "comment", "string", "number", "keyword", "function",
        "type", "variable", "operator", "constant", "property",
    ];

    for event in events {
        match event {
            HighlightEvent::Source { start, end } => {
                if current_pos < *start {
                    current_pos = *start;
                }
                if let Ok(text) = std::str::from_utf8(&bytes[*start..*end]) {
                    result.push_str(text);
                    current_pos = *end;
                }
            }
            HighlightEvent::HighlightStart(highlight) => {
                if let Some(name) = highlight_names.get(highlight.0) {
                    if let Some(color) = theme.get_ansi_color(name) {
                        result.push_str(&color.code);
                    }
                }
            }
            HighlightEvent::HighlightEnd => {
                result.push_str("\x1b[0m");
            }
        }
    }

    result
}

/// Format highlighted code as HTML
pub fn format_html(
    source_code: &str,
    events: &[HighlightEvent],
    theme: &Theme,
) -> String {
    let mut result = String::from("<pre><code>");
    let bytes = source_code.as_bytes();
    let highlight_names = [
        "comment", "string", "number", "keyword", "function",
        "type", "variable", "operator", "constant", "property",
    ];
    let mut highlight_stack: Vec<String> = Vec::new();

    for event in events {
        match event {
            HighlightEvent::Source { start, end } => {
                if let Ok(text) = std::str::from_utf8(&bytes[*start..*end]) {
                    // Escape HTML special characters
                    let escaped = text
                        .replace('&', "&amp;")
                        .replace('<', "&lt;")
                        .replace('>', "&gt;")
                        .replace('"', "&quot;")
                        .replace('\'', "&#39;");
                    result.push_str(&escaped);
                }
            }
            HighlightEvent::HighlightStart(highlight) => {
                if let Some(name) = highlight_names.get(highlight.0) {
                    if let Some(color) = theme.get_html_color(name) {
                        result.push_str(&format!("<span style=\"color: {}\">", color.hex));
                        highlight_stack.push(name.to_string());
                    }
                }
            }
            HighlightEvent::HighlightEnd => {
                if !highlight_stack.is_empty() {
                    highlight_stack.pop();
                    result.push_str("</span>");
                }
            }
        }
    }

    result.push_str("</code></pre>");
    result
}
