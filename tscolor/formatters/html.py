"""HTML formatter for web output."""
from typing import Iterator, List
from html import escape
from ..events import HighlightEvent, SourceEvent, HighlightStartEvent, HighlightEndEvent
from ..theme import Theme
from ..configuration import HighlightConfiguration


class HtmlFormatter:
    """Format highlighted code as HTML with inline styles.

    This formatter converts highlight events into HTML with span elements
    and inline CSS styles.

    Example:
        >>> formatter = HtmlFormatter(theme)
        >>> html = formatter.format(source, events, config)
        >>> # Use html in a web page
    """

    def __init__(self, theme: Theme, class_prefix: str = "ts-"):
        """Initialize the HTML formatter.

        Args:
            theme: Theme to use for coloring
            class_prefix: Prefix for CSS class names
        """
        self.theme = theme
        self.class_prefix = class_prefix

    def format(
        self,
        source: bytes,
        events: Iterator[HighlightEvent],
        config: HighlightConfiguration,
        inline_styles: bool = True,
    ) -> str:
        """Format highlight events as HTML.

        Args:
            source: The source code bytes
            events: Iterator of highlight events
            config: Highlight configuration with capture names
            inline_styles: Use inline styles instead of CSS classes

        Returns:
            HTML string
        """
        output = []

        for event in events:
            if isinstance(event, SourceEvent):
                # Extract and escape the source text
                text = source[event.start : event.end].decode("utf-8", errors="replace")
                escaped_text = escape(text)
                output.append(escaped_text)

            elif isinstance(event, HighlightStartEvent):
                # Get the capture name and color
                capture_name = config.highlight_names[event.index]
                color = self.theme.get_color(capture_name)

                if inline_styles:
                    output.append(f'<span style="color: {color};">')
                else:
                    css_class = self.class_prefix + capture_name.replace(".", "-")
                    output.append(f'<span class="{css_class}">')

            elif isinstance(event, HighlightEndEvent):
                output.append("</span>")

        return "".join(output)

    def format_complete(
        self,
        source: bytes,
        events: Iterator[HighlightEvent],
        config: HighlightConfiguration,
        title: str = "Syntax Highlighted Code",
        inline_styles: bool = True,
    ) -> str:
        """Format as a complete HTML document.

        Args:
            source: The source code bytes
            events: Iterator of highlight events
            config: Highlight configuration
            title: HTML document title
            inline_styles: Use inline styles instead of CSS classes

        Returns:
            Complete HTML document string
        """
        highlighted = self.format(source, events, config, inline_styles)

        bg_color = self.theme.background or "#ffffff"
        fg_color = self.theme.default_color

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <style>
        body {{
            background-color: {bg_color};
            color: {fg_color};
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 20px;
        }}
        pre {{
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        code {{
            font-family: 'Courier New', Courier, monospace;
        }}
"""

        # Add CSS classes if not using inline styles
        if not inline_styles:
            html += "        /* Syntax highlighting classes */\n"
            for capture_name in config.highlight_names:
                color = self.theme.get_color(capture_name)
                css_class = self.class_prefix + capture_name.replace(".", "-")
                html += f"        .{css_class} {{ color: {color}; }}\n"

        html += """    </style>
</head>
<body>
    <pre><code>"""
        html += highlighted
        html += """</code></pre>
</body>
</html>"""

        return html

    def generate_css(self, config: HighlightConfiguration) -> str:
        """Generate CSS stylesheet for the theme.

        Args:
            config: Highlight configuration with capture names

        Returns:
            CSS stylesheet string
        """
        css = [
            "/* Tree-sitter syntax highlighting styles */",
            f".{self.class_prefix}highlighted {{",
            f"    background-color: {self.theme.background or '#ffffff'};",
            f"    color: {self.theme.default_color};",
            "    font-family: 'Courier New', Courier, monospace;",
            "}",
            "",
        ]

        for capture_name in config.highlight_names:
            color = self.theme.get_color(capture_name)
            css_class = self.class_prefix + capture_name.replace(".", "-")
            css.append(f".{css_class} {{ color: {color}; }}")

        return "\n".join(css)
