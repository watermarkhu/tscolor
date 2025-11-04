"""ANSI color formatter for terminal output."""

from typing import Iterator, List
from ..events import HighlightEvent, SourceEvent, HighlightStartEvent, HighlightEndEvent
from ..theme import Theme
from ..configuration import HighlightConfiguration


class AnsiFormatter:
    """Format highlighted code with ANSI color codes for terminal output.

    This formatter converts highlight events into ANSI-colored text that can be
    displayed in a terminal.

    Example:
        >>> formatter = AnsiFormatter(theme)
        >>> text = formatter.format(source, events, config)
        >>> print(text)  # Displays colored output in terminal
    """

    def __init__(self, theme: Theme):
        """Initialize the ANSI formatter.

        Args:
            theme: Theme to use for coloring
        """
        self.theme = theme

    def format(
        self,
        source: bytes,
        events: Iterator[HighlightEvent],
        config: HighlightConfiguration,
    ) -> str:
        """Format highlight events as ANSI-colored text.

        Args:
            source: The source code bytes
            events: Iterator of highlight events
            config: Highlight configuration with capture names

        Returns:
            ANSI-colored string
        """
        output = []
        highlight_stack: List[int] = []

        for event in events:
            if isinstance(event, SourceEvent):
                # Extract the source text
                text = source[event.start : event.end].decode("utf-8", errors="replace")
                output.append(text)

            elif isinstance(event, HighlightStartEvent):
                # Get the capture name and color
                capture_name = config.highlight_names[event.index]
                color = self.theme.get_color(capture_name)
                ansi_code = self._hex_to_ansi(color)
                output.append(ansi_code)
                highlight_stack.append(event.index)

            elif isinstance(event, HighlightEndEvent):
                # Reset to previous color or default
                output.append(self._ansi_reset())
                if highlight_stack:
                    highlight_stack.pop()
                    # Restore previous highlight if nested
                    if highlight_stack:
                        prev_index = highlight_stack[-1]
                        capture_name = config.highlight_names[prev_index]
                        color = self.theme.get_color(capture_name)
                        ansi_code = self._hex_to_ansi(color)
                        output.append(ansi_code)

        # Ensure we reset at the end
        output.append(self._ansi_reset())
        return "".join(output)

    def _hex_to_ansi(self, hex_color: str) -> str:
        """Convert hex color to ANSI escape code.

        Args:
            hex_color: Hex color string like "#ff5555"

        Returns:
            ANSI escape code for 24-bit color
        """
        r, g, b = self.theme.hex_to_rgb(hex_color)
        return f"\033[38;2;{r};{g};{b}m"

    def _ansi_reset(self) -> str:
        """Get ANSI reset code.

        Returns:
            ANSI reset escape code
        """
        return "\033[0m"

    def format_with_background(
        self,
        source: bytes,
        events: Iterator[HighlightEvent],
        config: HighlightConfiguration,
    ) -> str:
        """Format with background color applied.

        Args:
            source: The source code bytes
            events: Iterator of highlight events
            config: Highlight configuration

        Returns:
            ANSI-colored string with background
        """
        if self.theme.background:
            r, g, b = self.theme.hex_to_rgb(self.theme.background)
            bg_code = f"\033[48;2;{r};{g};{b}m"
            return bg_code + self.format(source, events, config)
        return self.format(source, events, config)


def print_highlighted(
    source: bytes,
    events: Iterator[HighlightEvent],
    config: HighlightConfiguration,
    theme: Theme,
    use_background: bool = False,
) -> None:
    """Print highlighted code to stdout.

    Args:
        source: Source code bytes
        events: Highlight events
        config: Highlight configuration
        theme: Theme to use
        use_background: Whether to include background color
    """
    formatter = AnsiFormatter(theme)
    if use_background:
        text = formatter.format_with_background(source, events, config)
    else:
        text = formatter.format(source, events, config)
    print(text)
