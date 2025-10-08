use pyo3::prelude::*;

mod theme;
mod highlighter;
mod languages;

use theme::get_theme;
use highlighter::{Highlighter, format_terminal, format_html};
use languages::{init_languages, available_languages};

/// Highlight source code and output as terminal ANSI colors or HTML
///
/// # Arguments
///
/// * `code` - The source code to highlight
/// * `language` - The programming language (e.g., "python", "rust", "javascript", "json")
/// * `output_format` - Output format: "terminal" or "html"
/// * `theme_name` - Theme name: "dark" or "light" (default: "dark")
///
/// # Returns
///
/// Highlighted code as a string
#[pyfunction]
#[pyo3(signature = (code, language, output_format="terminal", theme_name="dark"))]
fn highlight(
    code: &str,
    language: &str,
    output_format: &str,
    theme_name: &str,
) -> PyResult<String> {
    // Create highlighter and initialize languages
    let mut highlighter = Highlighter::new();
    init_languages(&mut highlighter)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;

    // Get highlight events
    let events = highlighter.highlight(language, code)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;

    // Get theme
    let theme = get_theme(theme_name);

    // Format output
    let result = match output_format {
        "html" => format_html(code, &events, &theme),
        "terminal" | _ => format_terminal(code, &events, &theme),
    };

    Ok(result)
}

/// Get list of available programming languages
///
/// # Returns
///
/// List of language names
#[pyfunction]
fn get_available_languages() -> PyResult<Vec<String>> {
    Ok(available_languages())
}

/// Get list of available themes
///
/// # Returns
///
/// List of theme names
#[pyfunction]
fn get_available_themes() -> PyResult<Vec<String>> {
    Ok(vec!["dark".to_string(), "light".to_string()])
}

/// A Python module for syntax highlighting using tree-sitter.
#[pymodule]
fn tscolor(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(highlight, m)?)?;
    m.add_function(wrap_pyfunction!(get_available_languages, m)?)?;
    m.add_function(wrap_pyfunction!(get_available_themes, m)?)?;
    Ok(())
}
