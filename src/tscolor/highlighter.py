"""Core syntax highlighting engine."""
from typing import Iterator, Optional, Callable
import tree_sitter

from .configuration import HighlightConfiguration
from .events import HighlightEvent, SourceEvent, HighlightStartEvent, HighlightEndEvent


class Highlighter:
    """Syntax highlighter using tree-sitter.

    This class performs syntax highlighting by parsing source code with tree-sitter
    and generating highlight events based on the provided configuration.

    Example:
        >>> highlighter = Highlighter()
        >>> config = HighlightConfiguration(...)
        >>> source = b"def hello(): pass"
        >>> for event in highlighter.highlight(config, source):
        ...     # Process highlight events
        ...     pass
    """

    def __init__(self) -> None:
        """Initialize a new Highlighter instance."""
        self.parser = tree_sitter.Parser()

    def highlight(
        self,
        config: HighlightConfiguration,
        source: bytes,
        cancellation_flag: Optional[Callable[[], bool]] = None,
    ) -> Iterator[HighlightEvent]:
        """Highlight source code and yield highlight events.

        This method parses the source code and generates a sequence of highlight
        events that describe how to style different parts of the code.

        Args:
            config: Highlight configuration for the language
            source: Source code as bytes
            cancellation_flag: Optional callable that returns True to cancel highlighting

        Yields:
            HighlightEvent objects describing how to highlight the source

        Example:
            The events are emitted in this pattern:
            1. SourceEvent(start=0, end=3) - "def"
            2. HighlightStartEvent(index=0) - start keyword highlight
            3. HighlightEndEvent() - end keyword highlight
            4. SourceEvent(start=3, end=4) - " "
            5. ...
        """
        # Set the parser language
        self.parser.set_language(config.language)

        # Parse the source code
        tree = self.parser.parse(source)

        # Execute the highlights query
        captures = config.highlights_query.captures(tree.root_node)

        # Convert captures to a list for processing
        capture_list = list(captures)

        # Build a list of (start_byte, end_byte, highlight_name) tuples
        highlight_ranges = []
        for node, capture_name in capture_list:
            if cancellation_flag and cancellation_flag():
                return

            # Find the index of this capture name in the highlight names list
            if capture_name in config.highlight_names:
                highlight_index = config.highlight_names.index(capture_name)
                highlight_ranges.append(
                    (node.start_byte, node.end_byte, highlight_index, node)
                )

        # Sort by start position, then by end position (descending for proper nesting)
        highlight_ranges.sort(key=lambda x: (x[0], -x[1]))

        # Generate events from the highlight ranges
        yield from self._generate_events(source, highlight_ranges)

    def _generate_events(
        self,
        source: bytes,
        highlight_ranges: list,
    ) -> Iterator[HighlightEvent]:
        """Generate highlight events from sorted highlight ranges.

        This method processes the highlight ranges and generates a stream of events
        that properly handles overlapping and nested highlights.

        Args:
            source: The source code bytes
            highlight_ranges: List of (start_byte, end_byte, highlight_index, node) tuples

        Yields:
            HighlightEvent objects
        """
        if not highlight_ranges:
            # No highlights, just emit the entire source
            if len(source) > 0:
                yield SourceEvent(start=0, end=len(source))
            return

        # Track the current position and active highlights
        current_pos = 0
        active_stack = []  # Stack of (end_byte, highlight_index)

        # Create a list of all events (starts and ends) sorted by position
        events = []
        for start_byte, end_byte, highlight_index, node in highlight_ranges:
            events.append(("start", start_byte, end_byte, highlight_index))
            events.append(("end", end_byte, start_byte, highlight_index))

        # Sort events by position, with ends before starts at the same position
        events.sort(key=lambda x: (x[1], x[0] == "start"))

        for event_type, pos, other_pos, highlight_index in events:
            # Emit source for any gap before this event
            if current_pos < pos:
                yield SourceEvent(start=current_pos, end=pos)
                current_pos = pos

            if event_type == "start":
                # Start a new highlight
                yield HighlightStartEvent(index=highlight_index)
                active_stack.append((other_pos, highlight_index))
            else:  # end
                # End a highlight
                # Find and remove this highlight from the stack
                for i, (end_byte, h_idx) in enumerate(active_stack):
                    if end_byte == pos and h_idx == highlight_index:
                        active_stack.pop(i)
                        yield HighlightEndEvent()
                        break

        # Emit any remaining source
        if current_pos < len(source):
            yield SourceEvent(start=current_pos, end=len(source))
