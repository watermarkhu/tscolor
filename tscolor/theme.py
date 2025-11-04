"""Theme definitions for syntax highlighting."""

from typing import Dict, Optional, Tuple, List, Literal
from pathlib import Path
import yaml


ThemeCategory = Literal["light", "dark"]


class Theme:
    """Base class for syntax highlighting themes.

    A theme maps highlight capture names to colors. Colors can be specified
    as hex codes (e.g., "#ff5555").

    Attributes:
        name: Theme name
        category: Theme category ("light" or "dark")
        colors: Mapping from capture names to color values
        foreground: Default foreground color
        background: Optional background color
        selection: Optional selection color
        comment: Optional comment color (used as default for comments)
        author: Optional theme author
        description: Optional theme description
        url: Optional theme URL
    """

    def __init__(
        self,
        name: str,
        colors: Dict[str, str],
        category: ThemeCategory = "dark",
        foreground: str = "#f8f8f2",
        background: Optional[str] = None,
        selection: Optional[str] = None,
        comment: Optional[str] = None,
        author: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
    ):
        """Initialize a theme.

        Args:
            name: Theme name
            colors: Mapping from highlight capture names to hex colors
            category: Theme category ("light" or "dark")
            foreground: Default foreground color
            background: Optional background color
            selection: Optional selection color
            comment: Optional comment color
            author: Optional theme author
            description: Optional theme description
            url: Optional theme URL
        """
        self.name = name
        self.category = category
        self.colors = colors
        self.foreground = foreground
        self.background = background
        self.selection = selection
        self.comment = comment
        self.author = author
        self.description = description
        self.url = url

    @property
    def default_color(self) -> str:
        """Get the default color (alias for foreground)."""
        return self.foreground

    def get_color(self, capture_name: str) -> str:
        """Get the color for a capture name.

        Args:
            capture_name: The capture name from the query

        Returns:
            Hex color string
        """
        return self.colors.get(capture_name, self.foreground)

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple.

        Args:
            hex_color: Hex color string like "#ff5555"

        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def is_dark(self) -> bool:
        """Check if this is a dark theme.

        Returns:
            True if category is "dark"
        """
        return self.category == "dark"

    def is_light(self) -> bool:
        """Check if this is a light theme.

        Returns:
            True if category is "light"
        """
        return self.category == "light"

    @classmethod
    def from_yaml(cls, path: Path) -> "Theme":
        """Load a theme from a YAML file.

        Expected YAML format:
        ```yaml
        name: Theme Name
        category: dark  # or "light"
        author: Author Name
        description: Theme description
        url: https://example.com

        background: "#282a36"
        foreground: "#f8f8f2"
        selection: "#44475a"
        comment: "#6272a4"

        colors:
          keyword: "#ff79c6"
          function: "#50fa7b"
          string: "#f1fa8c"
          # ... more mappings
        ```

        Args:
            path: Path to the YAML theme file

        Returns:
            Theme instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML is invalid or missing required fields
        """
        if not path.exists():
            raise FileNotFoundError(f"Theme file not found: {path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid theme file: {path}")

        # Validate required fields
        if "name" not in data:
            raise ValueError(f"Theme file missing 'name' field: {path}")
        if "colors" not in data:
            raise ValueError(f"Theme file missing 'colors' field: {path}")

        return cls(
            name=data["name"],
            category=data.get("category", "dark"),
            colors=data["colors"],
            foreground=data.get("foreground", "#f8f8f2"),
            background=data.get("background"),
            selection=data.get("selection"),
            comment=data.get("comment"),
            author=data.get("author"),
            description=data.get("description"),
            url=data.get("url"),
        )

    def __repr__(self) -> str:
        """Return string representation of theme."""
        return f"Theme(name='{self.name}', category='{self.category}')"


# Theme registry
_THEMES: Dict[str, Theme] = {}
_themes_loaded = False


def _load_builtin_themes() -> None:
    """Load all built-in themes from the themes directory."""
    global _themes_loaded
    if _themes_loaded:
        return

    # Find the themes directory relative to this file
    themes_dir = Path(__file__).parent.parent / "themes"

    if themes_dir.exists():
        for theme_file in themes_dir.glob("*.yaml"):
            try:
                theme = Theme.from_yaml(theme_file)
                # Use lowercase name as key for case-insensitive lookup
                _THEMES[theme.name.lower()] = theme
            except Exception as e:
                # Log warning but don't fail if a theme file is invalid
                import warnings

                warnings.warn(f"Failed to load theme {theme_file}: {e}")

    _themes_loaded = True


def get_theme(name: str) -> Theme:
    """Get a theme by name.

    Themes are loaded from YAML files in the themes/ directory.
    Theme names are case-insensitive.

    Args:
        name: Theme name (e.g., "dracula", "github-light")

    Returns:
        Theme instance

    Raises:
        KeyError: If theme is not found

    Example:
        >>> theme = get_theme("dracula")
        >>> theme.category
        'dark'
    """
    _load_builtin_themes()

    theme_name = name.lower()
    if theme_name not in _THEMES:
        available = ", ".join(sorted(_THEMES.keys()))
        raise KeyError(f"Theme '{name}' not found. Available themes: {available}")
    return _THEMES[theme_name]


def list_themes(category: Optional[ThemeCategory] = None) -> List[str]:
    """List all available themes.

    Args:
        category: Optional filter by category ("light" or "dark")

    Returns:
        List of theme names

    Example:
        >>> list_themes()
        ['dracula', 'github-light', 'monokai']
        >>> list_themes(category='dark')
        ['dracula', 'monokai']
    """
    _load_builtin_themes()

    if category is None:
        return sorted(_THEMES.keys())

    return sorted(name for name, theme in _THEMES.items() if theme.category == category)


def register_theme(theme: Theme) -> None:
    """Register a custom theme.

    Args:
        theme: Theme instance to register

    Example:
        >>> custom_theme = Theme(
        ...     name="My Theme",
        ...     category="dark",
        ...     colors={"keyword": "#ff0000", ...}
        ... )
        >>> register_theme(custom_theme)
        >>> theme = get_theme("my theme")
    """
    _THEMES[theme.name.lower()] = theme


# Legacy compatibility
THEMES = _THEMES


def get_theme_info(name: str) -> Dict[str, Optional[str]]:
    """Get information about a theme.

    Args:
        name: Theme name

    Returns:
        Dictionary with theme metadata

    Example:
        >>> info = get_theme_info("dracula")
        >>> info['category']
        'dark'
        >>> info['author']
        'Dracula Theme'
    """
    theme = get_theme(name)
    return {
        "name": theme.name,
        "category": theme.category,
        "author": theme.author,
        "description": theme.description,
        "url": theme.url,
        "background": theme.background,
        "foreground": theme.foreground,
    }
