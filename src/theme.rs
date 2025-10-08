use std::collections::HashMap;

/// Represents an ANSI color code for terminal output
#[derive(Debug, Clone)]
pub struct AnsiColor {
    pub code: String,
}

impl AnsiColor {
    pub fn new(code: &str) -> Self {
        Self {
            code: code.to_string(),
        }
    }

    pub fn rgb(r: u8, g: u8, b: u8) -> Self {
        Self {
            code: format!("\x1b[38;2;{};{};{}m", r, g, b),
        }
    }

    pub fn reset() -> Self {
        Self {
            code: "\x1b[0m".to_string(),
        }
    }
}

/// Represents an HTML color for HTML output
#[derive(Debug, Clone)]
pub struct HtmlColor {
    pub hex: String,
}

impl HtmlColor {
    pub fn new(hex: &str) -> Self {
        Self {
            hex: hex.to_string(),
        }
    }
}

/// Theme configuration for syntax highlighting
#[derive(Debug, Clone)]
pub struct Theme {
    pub name: String,
    pub ansi_colors: HashMap<String, AnsiColor>,
    pub html_colors: HashMap<String, HtmlColor>,
}

impl Theme {
    /// Create a dark theme (default)
    pub fn dark() -> Self {
        let mut ansi_colors = HashMap::new();
        ansi_colors.insert("comment".to_string(), AnsiColor::rgb(128, 128, 128));
        ansi_colors.insert("string".to_string(), AnsiColor::rgb(152, 195, 121));
        ansi_colors.insert("number".to_string(), AnsiColor::rgb(209, 154, 102));
        ansi_colors.insert("keyword".to_string(), AnsiColor::rgb(198, 120, 221));
        ansi_colors.insert("function".to_string(), AnsiColor::rgb(97, 175, 239));
        ansi_colors.insert("type".to_string(), AnsiColor::rgb(229, 192, 123));
        ansi_colors.insert("variable".to_string(), AnsiColor::rgb(224, 108, 117));
        ansi_colors.insert("operator".to_string(), AnsiColor::rgb(86, 182, 194));
        ansi_colors.insert("constant".to_string(), AnsiColor::rgb(209, 154, 102));
        ansi_colors.insert("property".to_string(), AnsiColor::rgb(224, 108, 117));

        let mut html_colors = HashMap::new();
        html_colors.insert("comment".to_string(), HtmlColor::new("#808080"));
        html_colors.insert("string".to_string(), HtmlColor::new("#98c379"));
        html_colors.insert("number".to_string(), HtmlColor::new("#d19a66"));
        html_colors.insert("keyword".to_string(), HtmlColor::new("#c678dd"));
        html_colors.insert("function".to_string(), HtmlColor::new("#61afef"));
        html_colors.insert("type".to_string(), HtmlColor::new("#e5c07b"));
        html_colors.insert("variable".to_string(), HtmlColor::new("#e06c75"));
        html_colors.insert("operator".to_string(), HtmlColor::new("#56b6c2"));
        html_colors.insert("constant".to_string(), HtmlColor::new("#d19a66"));
        html_colors.insert("property".to_string(), HtmlColor::new("#e06c75"));

        Self {
            name: "dark".to_string(),
            ansi_colors,
            html_colors,
        }
    }

    /// Create a light theme
    pub fn light() -> Self {
        let mut ansi_colors = HashMap::new();
        ansi_colors.insert("comment".to_string(), AnsiColor::rgb(160, 160, 160));
        ansi_colors.insert("string".to_string(), AnsiColor::rgb(80, 161, 79));
        ansi_colors.insert("number".to_string(), AnsiColor::rgb(152, 104, 1));
        ansi_colors.insert("keyword".to_string(), AnsiColor::rgb(166, 38, 164));
        ansi_colors.insert("function".to_string(), AnsiColor::rgb(0, 84, 166));
        ansi_colors.insert("type".to_string(), AnsiColor::rgb(152, 118, 24));
        ansi_colors.insert("variable".to_string(), AnsiColor::rgb(152, 24, 34));
        ansi_colors.insert("operator".to_string(), AnsiColor::rgb(0, 128, 128));
        ansi_colors.insert("constant".to_string(), AnsiColor::new("#d19a66"));
        ansi_colors.insert("property".to_string(), AnsiColor::rgb(152, 24, 34));

        let mut html_colors = HashMap::new();
        html_colors.insert("comment".to_string(), HtmlColor::new("#a0a0a0"));
        html_colors.insert("string".to_string(), HtmlColor::new("#50a14f"));
        html_colors.insert("number".to_string(), HtmlColor::new("#986801"));
        html_colors.insert("keyword".to_string(), HtmlColor::new("#a626a4"));
        html_colors.insert("function".to_string(), HtmlColor::new("#0054a6"));
        html_colors.insert("type".to_string(), HtmlColor::new("#987618"));
        html_colors.insert("variable".to_string(), HtmlColor::new("#981822"));
        html_colors.insert("operator".to_string(), HtmlColor::new("#008080"));
        html_colors.insert("constant".to_string(), HtmlColor::new("#986801"));
        html_colors.insert("property".to_string(), HtmlColor::new("#981822"));

        Self {
            name: "light".to_string(),
            ansi_colors,
            html_colors,
        }
    }

    pub fn get_ansi_color(&self, highlight_name: &str) -> Option<&AnsiColor> {
        self.ansi_colors.get(highlight_name)
    }

    pub fn get_html_color(&self, highlight_name: &str) -> Option<&HtmlColor> {
        self.html_colors.get(highlight_name)
    }
}

pub fn get_theme(name: &str) -> Theme {
    match name {
        "light" => Theme::light(),
        _ => Theme::dark(),
    }
}
