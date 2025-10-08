use std::collections::HashMap;
use std::fs;
use std::path::Path;
use serde::{Deserialize, Serialize};

/// RGB color values for terminal ANSI colors
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct RgbColor {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

/// Represents an ANSI color code for terminal output
#[derive(Debug, Clone)]
pub struct AnsiColor {
    pub code: String,
}

impl AnsiColor {
    pub fn from_rgb(rgb: &RgbColor) -> Self {
        Self {
            code: format!("\x1b[38;2;{};{};{}m", rgb.r, rgb.g, rgb.b),
        }
    }

    pub fn from_hex(hex: &str) -> Result<Self, String> {
        let rgb = hex_to_rgb(hex)?;
        Ok(Self::from_rgb(&rgb))
    }
}

/// Convert hex color string to RGB values
fn hex_to_rgb(hex: &str) -> Result<RgbColor, String> {
    let hex = hex.trim_start_matches('#');
    
    if hex.len() != 6 {
        return Err(format!("Invalid hex color format: #{}", hex));
    }
    
    let r = u8::from_str_radix(&hex[0..2], 16)
        .map_err(|_| format!("Invalid hex color format: #{}", hex))?;
    let g = u8::from_str_radix(&hex[2..4], 16)
        .map_err(|_| format!("Invalid hex color format: #{}", hex))?;
    let b = u8::from_str_radix(&hex[4..6], 16)
        .map_err(|_| format!("Invalid hex color format: #{}", hex))?;
    
    Ok(RgbColor { r, g, b })
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

/// JSON theme configuration for deserialization
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ThemeConfig {
    pub name: String,
    pub description: Option<String>,
    pub colors: HashMap<String, String>, // All colors as hex strings
}

/// Theme configuration for syntax highlighting
#[derive(Debug, Clone)]
pub struct Theme {
    pub name: String,
    pub ansi_colors: HashMap<String, AnsiColor>,
    pub html_colors: HashMap<String, HtmlColor>,
}

impl ThemeConfig {
    /// Convert ThemeConfig to Theme
    pub fn to_theme(self) -> Theme {
        let mut ansi_colors = HashMap::new();
        let mut html_colors = HashMap::new();

        for (name, hex) in self.colors {
            // Create ANSI color from hex
            if let Ok(ansi_color) = AnsiColor::from_hex(&hex) {
                ansi_colors.insert(name.clone(), ansi_color);
            }
            
            // Create HTML color (just use hex directly)
            html_colors.insert(name, HtmlColor::new(&hex));
        }

        Theme {
            name: self.name,
            ansi_colors,
            html_colors,
        }
    }
}

impl Theme {
    /// Load theme from JSON file
    pub fn from_json_file<P: AsRef<Path>>(path: P) -> Result<Self, String> {
        let content = fs::read_to_string(path)
            .map_err(|e| format!("Failed to read theme file: {}", e))?;
        
        let config: ThemeConfig = serde_json::from_str(&content)
            .map_err(|e| format!("Failed to parse theme JSON: {}", e))?;
        
        Ok(config.to_theme())
    }

    /// Create a dark theme (default) - fallback if JSON loading fails
    pub fn dark() -> Self {
        // Fallback dark theme with hardcoded values
        let config = ThemeConfig {
            name: "dark".to_string(),
            description: Some("Dark theme (fallback)".to_string()),
            colors: [
                ("comment", "#808080"),
                ("string", "#98c379"),
                ("number", "#d19a66"),
                ("keyword", "#c678dd"),
                ("function", "#61afef"),
                ("type", "#e5c07b"),
                ("variable", "#e06c75"),
                ("operator", "#56b6c2"),
                ("constant", "#d19a66"),
                ("property", "#e06c75"),
            ].iter().map(|(k, v)| (k.to_string(), v.to_string())).collect(),
        };
        config.to_theme()
    }

    /// Create a light theme - fallback if JSON loading fails
    pub fn light() -> Self {
        // Fallback light theme with hardcoded values
        let config = ThemeConfig {
            name: "light".to_string(),
            description: Some("Light theme (fallback)".to_string()),
            colors: [
                ("comment", "#a0a0a0"),
                ("string", "#50a14f"),
                ("number", "#986801"),
                ("keyword", "#a626a4"),
                ("function", "#0054a6"),
                ("type", "#987618"),
                ("variable", "#981822"),
                ("operator", "#008080"),
                ("constant", "#986801"),
                ("property", "#981822"),
            ].iter().map(|(k, v)| (k.to_string(), v.to_string())).collect(),
        };
        config.to_theme()
    }

    pub fn get_ansi_color(&self, highlight_name: &str) -> Option<&AnsiColor> {
        self.ansi_colors.get(highlight_name)
    }

    pub fn get_html_color(&self, highlight_name: &str) -> Option<&HtmlColor> {
        self.html_colors.get(highlight_name)
    }
}

/// Load theme from JSON file or fallback to hardcoded themes
pub fn load_theme(name: &str) -> Theme {
    // Try to load from JSON file first
    let theme_path = format!("themes/{}.json", name);
    if let Ok(theme) = Theme::from_json_file(&theme_path) {
        return theme;
    }

    // Fallback to hardcoded themes
    match name {
        "light" => Theme::light(),
        _ => Theme::dark(),
    }
}

/// Get available theme names by scanning themes directory and including built-in themes
pub fn get_available_themes() -> Vec<String> {
    let mut themes = Vec::new();
    
    // Add built-in themes
    themes.push("dark".to_string());
    themes.push("light".to_string());
    
    // Scan themes directory for JSON files
    if let Ok(entries) = fs::read_dir("themes") {
        for entry in entries.flatten() {
            if let Some(filename) = entry.file_name().to_str() {
                if filename.ends_with(".json") {
                    let theme_name = filename.trim_end_matches(".json");
                    if !themes.contains(&theme_name.to_string()) {
                        themes.push(theme_name.to_string());
                    }
                }
            }
        }
    }
    
    themes
}

// Backward compatibility
pub fn get_theme(name: &str) -> Theme {
    load_theme(name)
}
