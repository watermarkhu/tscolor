use std::path::Path;

/// Detect programming language from file extension
///
/// # Arguments
///
/// * `path` - Path to the file
///
/// # Returns
///
/// Detected language name, or None if not recognized
pub fn detect_language(path: &Path) -> Option<String> {
    path.extension()
        .and_then(|ext| ext.to_str())
        .and_then(|ext| match ext {
            "py" | "pyw" => Some("python"),
            "rs" => Some("rust"),
            "js" | "jsx" | "mjs" | "cjs" => Some("javascript"),
            "json" | "jsonc" => Some("json"),
            "ts" => Some("typescript"),
            "tsx" => Some("typescript"),
            _ => None,
        })
        .map(|s| s.to_string())
}

/// Get list of supported file extensions
pub fn supported_extensions() -> &'static str {
    ".py, .pyw, .rs, .js, .jsx, .mjs, .cjs, .json, .jsonc, .ts, .tsx"
}
