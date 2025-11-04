"""Tests for theme loading and management."""

import pytest
from pathlib import Path
from tscolor import Theme, get_theme, list_themes, register_theme, get_theme_info


class TestThemeLoading:
    """Test theme loading from YAML files."""

    def test_get_dracula_theme(self):
        """Test loading Dracula theme."""
        theme = get_theme("dracula")
        assert theme.name == "Dracula"
        assert theme.category == "dark"
        assert theme.is_dark()
        assert not theme.is_light()
        assert theme.background == "#282a36"
        assert theme.foreground == "#f8f8f2"

    def test_get_github_light_theme(self):
        """Test loading GitHub Light theme."""
        theme = get_theme("github-light")
        assert theme.name == "github-light"
        assert theme.category == "light"
        assert theme.is_light()
        assert not theme.is_dark()
        assert theme.background == "#ffffff"

    def test_get_monokai_theme(self):
        """Test loading Monokai theme."""
        theme = get_theme("monokai")
        assert theme.name == "Monokai"
        assert theme.category == "dark"
        assert theme.background == "#272822"

    def test_theme_case_insensitive(self):
        """Test that theme lookup is case-insensitive."""
        theme1 = get_theme("dracula")
        theme2 = get_theme("DRACULA")
        theme3 = get_theme("Dracula")
        assert theme1.name == theme2.name == theme3.name

    def test_invalid_theme_raises_error(self):
        """Test that invalid theme name raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            get_theme("nonexistent-theme")


class TestThemeListing:
    """Test theme listing functions."""

    def test_list_all_themes(self):
        """Test listing all themes."""
        themes = list_themes()
        assert isinstance(themes, list)
        assert len(themes) >= 3  # At least dracula, github-light, monokai
        assert "dracula" in themes
        assert "github-light" in themes
        assert "monokai" in themes

    def test_list_dark_themes(self):
        """Test listing only dark themes."""
        themes = list_themes(category="dark")
        assert "dracula" in themes
        assert "monokai" in themes
        assert "github-light" not in themes

    def test_list_light_themes(self):
        """Test listing only light themes."""
        themes = list_themes(category="light")
        assert "github-light" in themes
        assert "dracula" not in themes
        assert "monokai" not in themes


class TestThemeInfo:
    """Test theme information retrieval."""

    def test_get_theme_info(self):
        """Test getting theme information."""
        info = get_theme_info("dracula")
        assert info["name"] == "Dracula"
        assert info["category"] == "dark"
        assert info["author"] == "Dracula Theme"
        assert info["background"] == "#282a36"
        assert info["foreground"] == "#f8f8f2"


class TestThemeColors:
    """Test theme color functionality."""

    def test_get_color_existing(self):
        """Test getting a color that exists in theme."""
        theme = get_theme("dracula")
        assert theme.get_color("keyword") == "#ff79c6"
        assert theme.get_color("string") == "#f1fa8c"
        assert theme.get_color("function") == "#50fa7b"

    def test_get_color_fallback(self):
        """Test that missing colors fall back to foreground."""
        theme = get_theme("dracula")
        nonexistent = theme.get_color("nonexistent.capture")
        assert nonexistent == theme.foreground

    def test_hex_to_rgb(self):
        """Test hex to RGB conversion."""
        theme = get_theme("dracula")
        # Pink color: #ff79c6
        r, g, b = theme.hex_to_rgb("#ff79c6")
        assert r == 255
        assert g == 121
        assert b == 198

    def test_hex_to_rgb_without_hash(self):
        """Test hex to RGB conversion without # prefix."""
        theme = get_theme("dracula")
        r, g, b = theme.hex_to_rgb("ff79c6")
        assert r == 255
        assert g == 121
        assert b == 198


class TestCustomTheme:
    """Test custom theme registration."""

    def test_register_custom_theme(self):
        """Test registering a custom theme."""
        custom = Theme(
            name="Test Theme",
            category="dark",
            colors={
                "keyword": "#ff0000",
                "string": "#00ff00",
            },
            foreground="#ffffff",
            background="#000000",
        )

        register_theme(custom)
        retrieved = get_theme("test theme")
        assert retrieved.name == "Test Theme"
        assert retrieved.get_color("keyword") == "#ff0000"

    def test_custom_theme_in_list(self):
        """Test that registered theme appears in listing."""
        custom = Theme(
            name="Another Test Theme",
            category="light",
            colors={},
        )

        register_theme(custom)
        themes = list_themes()
        assert "another test theme" in themes


class TestThemeYAML:
    """Test Theme.from_yaml() method."""

    def test_from_yaml_valid(self, themes_dir):
        """Test loading theme from YAML file."""
        theme_file = themes_dir / "dracula.yaml"
        if theme_file.exists():
            theme = Theme.from_yaml(theme_file)
            assert theme.name == "Dracula"
            assert theme.category == "dark"
            assert isinstance(theme.colors, dict)
            assert len(theme.colors) > 0

    def test_from_yaml_missing_file(self):
        """Test that missing file raises error."""
        with pytest.raises(FileNotFoundError):
            Theme.from_yaml(Path("/nonexistent/theme.yaml"))


class TestThemeRepresentation:
    """Test theme string representation."""

    def test_theme_repr(self):
        """Test __repr__ method."""
        theme = get_theme("dracula")
        repr_str = repr(theme)
        assert "Dracula" in repr_str
        assert "dark" in repr_str
