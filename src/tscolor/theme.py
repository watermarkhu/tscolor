"""Theme definitions for syntax highlighting."""
from typing import Dict, Optional, Tuple
from pathlib import Path
import json


class Theme:
    """Base class for syntax highlighting themes.

    A theme maps highlight capture names to colors. Colors can be specified
    as hex codes (e.g., "#ff5555") or RGB tuples.

    Attributes:
        name: Theme name
        colors: Mapping from capture names to color values
        default_color: Default color for unmatched captures
        background: Optional background color
    """

    def __init__(
        self,
        name: str,
        colors: Dict[str, str],
        default_color: str = "#f8f8f2",
        background: Optional[str] = None,
    ):
        """Initialize a theme.

        Args:
            name: Theme name
            colors: Mapping from highlight capture names to hex colors
            default_color: Default color for captures not in the mapping
            background: Optional background color
        """
        self.name = name
        self.colors = colors
        self.default_color = default_color
        self.background = background

    def get_color(self, capture_name: str) -> str:
        """Get the color for a capture name.

        Args:
            capture_name: The capture name from the query

        Returns:
            Hex color string
        """
        return self.colors.get(capture_name, self.default_color)

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple.

        Args:
            hex_color: Hex color string like "#ff5555"

        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @classmethod
    def from_json(cls, path: Path) -> "Theme":
        """Load a theme from a JSON file.

        Expected JSON format:
        {
            "name": "Theme Name",
            "colors": {
                "keyword": "#ff79c6",
                "function": "#50fa7b",
                ...
            },
            "default_color": "#f8f8f2",
            "background": "#282a36"
        }

        Args:
            path: Path to the JSON theme file

        Returns:
            Theme instance
        """
        with open(path, "r") as f:
            data = json.load(f)

        return cls(
            name=data["name"],
            colors=data["colors"],
            default_color=data.get("default_color", "#f8f8f2"),
            background=data.get("background"),
        )


class DraculaTheme(Theme):
    """Dracula theme for syntax highlighting.

    Official Dracula theme colors from https://draculatheme.com/
    """

    # Official Dracula color palette
    BACKGROUND = "#282a36"
    CURRENT_LINE = "#44475a"
    FOREGROUND = "#f8f8f2"
    COMMENT = "#6272a4"
    CYAN = "#8be9fd"
    GREEN = "#50fa7b"
    ORANGE = "#ffb86c"
    PINK = "#ff79c6"
    PURPLE = "#bd93f9"
    RED = "#ff5555"
    YELLOW = "#f1fa8c"

    def __init__(self):
        """Initialize the Dracula theme with standard color mappings."""
        colors = {
            # Keywords and control flow
            "keyword": self.PINK,
            "keyword.control": self.PINK,
            "keyword.function": self.CYAN,
            "keyword.operator": self.PINK,
            "keyword.return": self.PINK,
            "keyword.import": self.PINK,
            # Functions and methods
            "function": self.GREEN,
            "function.builtin": self.GREEN,
            "function.method": self.GREEN,
            "function.call": self.GREEN,
            "method": self.GREEN,
            "method.call": self.GREEN,
            # Types
            "type": self.CYAN,
            "type.builtin": self.CYAN,
            "class": self.CYAN,
            # Constants and literals
            "constant": self.PURPLE,
            "constant.builtin": self.PURPLE,
            "number": self.PURPLE,
            "boolean": self.PURPLE,
            "float": self.PURPLE,
            "integer": self.PURPLE,
            # Strings
            "string": self.YELLOW,
            "string.escape": self.PINK,
            "character": self.YELLOW,
            # Comments
            "comment": self.COMMENT,
            "comment.line": self.COMMENT,
            "comment.block": self.COMMENT,
            # Variables
            "variable": self.FOREGROUND,
            "variable.builtin": self.PURPLE,
            "variable.parameter": self.ORANGE,
            "parameter": self.ORANGE,
            # Operators
            "operator": self.PINK,
            # Punctuation
            "punctuation": self.FOREGROUND,
            "punctuation.bracket": self.FOREGROUND,
            "punctuation.delimiter": self.FOREGROUND,
            # Properties and attributes
            "property": self.FOREGROUND,
            "attribute": self.GREEN,
            # Tags (HTML, XML, etc.)
            "tag": self.PINK,
            "tag.attribute": self.GREEN,
            # Markup
            "markup.heading": self.PURPLE,
            "markup.bold": self.ORANGE,
            "markup.italic": self.YELLOW,
            "markup.link": self.CYAN,
            "markup.quote": self.YELLOW,
            "markup.list": self.CYAN,
            # Special
            "constructor": self.CYAN,
            "module": self.FOREGROUND,
            "namespace": self.FOREGROUND,
            "label": self.CYAN,
            "annotation": self.YELLOW,
            "decorator": self.GREEN,
            # Errors
            "error": self.RED,
            "warning": self.ORANGE,
        }

        super().__init__(
            name="Dracula",
            colors=colors,
            default_color=self.FOREGROUND,
            background=self.BACKGROUND,
        )


# Default theme registry
THEMES: Dict[str, Theme] = {
    "dracula": DraculaTheme(),
}


def get_theme(name: str) -> Theme:
    """Get a theme by name.

    Args:
        name: Theme name (case-insensitive)

    Returns:
        Theme instance

    Raises:
        KeyError: If theme is not found
    """
    theme_name = name.lower()
    if theme_name not in THEMES:
        available = ", ".join(THEMES.keys())
        raise KeyError(
            f"Theme '{name}' not found. Available themes: {available}"
        )
    return THEMES[theme_name]
