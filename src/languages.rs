use crate::highlighter::Highlighter;

/// Initialize available languages based on compiled features
pub fn init_languages(highlighter: &mut Highlighter) -> Result<(), String> {
    #[cfg(feature = "python")]
    {
        register_python(highlighter)?;
    }

    #[cfg(feature = "rust")]
    {
        register_rust(highlighter)?;
    }

    #[cfg(feature = "javascript")]
    {
        register_javascript(highlighter)?;
    }

    #[cfg(feature = "json")]
    {
        register_json(highlighter)?;
    }

    #[cfg(not(any(feature = "python", feature = "rust", feature = "javascript", feature = "json")))]
    {
        let _ = highlighter; // Suppress warning when no features are enabled
    }

    Ok(())
}

#[cfg(feature = "python")]
fn register_python(highlighter: &mut Highlighter) -> Result<(), String> {
    let language = tree_sitter_python::LANGUAGE;
    let highlights = tree_sitter_python::HIGHLIGHTS_QUERY;
    highlighter.register_language(
        "python",
        language.into(),
        highlights,
        "",
        "",
    )
}

#[cfg(feature = "rust")]
fn register_rust(highlighter: &mut Highlighter) -> Result<(), String> {
    let language = tree_sitter_rust::LANGUAGE;
    let highlights = tree_sitter_rust::HIGHLIGHTS_QUERY;
    highlighter.register_language(
        "rust",
        language.into(),
        highlights,
        "",
        "",
    )
}

#[cfg(feature = "javascript")]
fn register_javascript(highlighter: &mut Highlighter) -> Result<(), String> {
    let language = tree_sitter_javascript::LANGUAGE;
    let highlights = tree_sitter_javascript::HIGHLIGHT_QUERY;
    highlighter.register_language(
        "javascript",
        language.into(),
        highlights,
        "",
        "",
    )
}

#[cfg(feature = "json")]
fn register_json(highlighter: &mut Highlighter) -> Result<(), String> {
    let language = tree_sitter_json::LANGUAGE;
    let highlights = tree_sitter_json::HIGHLIGHTS_QUERY;
    highlighter.register_language(
        "json",
        language.into(),
        highlights,
        "",
        "",
    )
}

/// Get list of available languages
pub fn available_languages() -> Vec<String> {
    let languages = Vec::new();

    #[cfg(feature = "python")]
    let languages = {
        let mut langs = languages;
        langs.push("python".to_string());
        langs
    };

    #[cfg(feature = "rust")]
    let languages = {
        let mut langs = languages;
        langs.push("rust".to_string());
        langs
    };

    #[cfg(feature = "javascript")]
    let languages = {
        let mut langs = languages;
        langs.push("javascript".to_string());
        langs
    };

    #[cfg(feature = "json")]
    let languages = {
        let mut langs = languages;
        langs.push("json".to_string());
        langs
    };

    languages
}
