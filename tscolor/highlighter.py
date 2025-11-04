"""Enhanced syntax highlighting engine with multi-layer support."""

from typing import Iterator, Optional, Callable, Dict, Set, Tuple, List
import tree_sitter

from .configuration import HighlightConfiguration
from .events import HighlightEvent, SourceEvent, HighlightStartEvent, HighlightEndEvent
from .layer import HighlightLayer, SortableEvent


class HighlighterV2:
    """Enhanced syntax highlighter with multi-layer support.

    This highlighter supports:
    - Language injection (embedding one language in another)
    - Local variable scope tracking
    - Multi-layer processing with proper prioritization
    - Overlapping highlight deduplication

    Example:
        >>> highlighter = HighlighterV2()
        >>> config = HighlightConfiguration(...)
        >>> source = b"def hello(): pass"
        >>> for event in highlighter.highlight(config, source):
        ...     # Process highlight events
        ...     pass
    """

    def __init__(self) -> None:
        """Initialize a new highlighter instance."""
        self.parser = tree_sitter.Parser()
        self._injection_configs: Dict[str, HighlightConfiguration] = {}

    def register_injection_language(
        self, name: str, config: HighlightConfiguration
    ) -> None:
        """Register a language configuration for injection support.

        Args:
            name: Language name (e.g., "javascript", "python")
            config: Highlight configuration for the language
        """
        self._injection_configs[name] = config

    def highlight(
        self,
        config: HighlightConfiguration,
        source: bytes,
        cancellation_flag: Optional[Callable[[], bool]] = None,
    ) -> Iterator[HighlightEvent]:
        """Highlight source code and yield highlight events.

        Args:
            config: Highlight configuration for the language
            source: Source code as bytes
            cancellation_flag: Optional callable that returns True to cancel

        Yields:
            HighlightEvent objects describing how to highlight the source
        """
        # Set the parser language
        self.parser.language = config.language

        # Parse the source code
        tree = self.parser.parse(source)

        # Create the base layer
        base_layer = HighlightLayer(config=config, tree=tree, depth=0)

        # Collect all layers (base + injections)
        layers = [base_layer]

        # Process language injections if available
        if config.injections_query:
            injection_layers = self._extract_injections(config, tree, source, depth=1)
            layers.extend(injection_layers)

        # Extract and sort all highlight events from all layers
        events = self._collect_events_from_layers(layers, source)

        # Deduplicate and emit events
        yield from self._emit_events(source, events, cancellation_flag)

    def _extract_injections(
        self,
        config: HighlightConfiguration,
        tree: tree_sitter.Tree,
        source: bytes,
        depth: int,
    ) -> List[HighlightLayer]:
        """Extract language injection layers.

        Args:
            config: Configuration with injection query
            tree: Parsed syntax tree
            source: Source code
            depth: Current nesting depth

        Returns:
            List of injection layers
        """
        layers = []

        if not config.injections_query:
            return layers

        # Execute injection query using QueryCursor
        cursor = tree_sitter.QueryCursor(config.injections_query)
        matches = cursor.matches(tree.root_node)

        # Group captures by language
        language_ranges: Dict[str, List[Tuple[int, int]]] = {}

        # Convert matches to (node, capture_name) tuples and process
        for pattern_index, captures_dict in matches:
            for capture_name, nodes in captures_dict.items():
                for node in nodes:
                    # Look for injection.language captures
                    if capture_name == "injection.language":
                        lang_name = node.text.decode("utf-8", errors="replace")
                        if lang_name in self._injection_configs:
                            if lang_name not in language_ranges:
                                language_ranges[lang_name] = []

                    # Look for injection.content captures
                    elif capture_name == "injection.content":
                        # Find which language this belongs to
                        # For simplicity, we'll use the most recently seen language
                        # A more sophisticated approach would match them by pattern
                        for lang_name in language_ranges:
                            language_ranges[lang_name].append(
                                (node.start_byte, node.end_byte)
                            )

        # Create layers for each injected language
        for lang_name, ranges in language_ranges.items():
            if lang_name in self._injection_configs:
                inj_config = self._injection_configs[lang_name]

                # Parse the injected content
                self.parser.language = inj_config.language

                # For each range, create a layer
                for start, end in ranges:
                    content = source[start:end]
                    inj_tree = self.parser.parse(content)

                    layer = HighlightLayer(
                        config=inj_config,
                        tree=inj_tree,
                        depth=depth,
                        ranges=[(start, end)],
                    )
                    layers.append(layer)

        return layers

    def _collect_events_from_layers(
        self, layers: List[HighlightLayer], source: bytes
    ) -> List[SortableEvent]:
        """Collect and sort events from all layers.

        Args:
            layers: List of highlight layers
            source: Source code bytes

        Returns:
            Sorted list of events
        """
        events = []

        for layer in layers:
            # Extract highlights from this layer
            for capture_data in layer.extract_highlights():
                node = capture_data.node
                capture_name = capture_data.capture_name

                # Handle local scope captures
                if capture_name == "local.scope":
                    layer.process_local_scope(node, capture_name)
                    continue
                elif capture_name == "local.definition":
                    layer.process_local_definition(node, capture_name)
                    continue
                elif capture_name == "local.reference":
                    # Resolve reference to definition
                    highlight_index = layer.resolve_local_reference(node, capture_name)
                    if highlight_index is None:
                        continue
                else:
                    # Regular highlight capture
                    if capture_name not in layer.config.capture_index_map:
                        continue
                    highlight_index = layer.config.capture_index_map[capture_name]

                # Create start and end events
                start_event = SortableEvent(
                    sort_key=layer.sort_key(node.start_byte, is_end=False),
                    event_type="start",
                    position=node.start_byte,
                    highlight_index=highlight_index,
                    depth=layer.depth,
                    range=(node.start_byte, node.end_byte),
                )

                end_event = SortableEvent(
                    sort_key=layer.sort_key(node.end_byte, is_end=True),
                    event_type="end",
                    position=node.end_byte,
                    highlight_index=highlight_index,
                    depth=layer.depth,
                    range=(node.start_byte, node.end_byte),
                )

                events.append(start_event)
                events.append(end_event)

        # Sort all events
        events.sort()

        return events

    def _emit_events(
        self,
        source: bytes,
        sorted_events: List[SortableEvent],
        cancellation_flag: Optional[Callable[[], bool]],
    ) -> Iterator[HighlightEvent]:
        """Emit highlight events, handling overlaps and deduplication.

        Args:
            source: Source code bytes
            sorted_events: Sorted list of events
            cancellation_flag: Optional cancellation check

        Yields:
            HighlightEvent objects
        """
        if not sorted_events:
            # No highlights, emit entire source
            if len(source) > 0:
                yield SourceEvent(start=0, end=len(source))
            return

        current_pos = 0
        active_highlights: List[Tuple[int, int, int]] = []  # (end, index, depth)
        seen_ranges: Set[Tuple[int, int, int]] = set()  # (start, end, depth)

        for event in sorted_events:
            if cancellation_flag and cancellation_flag():
                return

            # Skip duplicates from overlapping layers
            range_key = (event.range[0], event.range[1], event.depth)
            if event.event_type == "start" and range_key in seen_ranges:
                # Skip this highlight as it's already been processed
                continue

            # Emit source gap before this event
            if current_pos < event.position:
                yield SourceEvent(start=current_pos, end=event.position)
                current_pos = event.position

            if event.event_type == "start":
                # Mark this range as seen
                seen_ranges.add(range_key)

                # Emit highlight start
                yield HighlightStartEvent(index=event.highlight_index)
                active_highlights.append(
                    (event.range[1], event.highlight_index, event.depth)
                )

            else:  # end
                # Find and remove the matching highlight
                for i, (end_pos, h_idx, depth) in enumerate(active_highlights):
                    if (
                        end_pos == event.position
                        and h_idx == event.highlight_index
                        and depth == event.depth
                    ):
                        active_highlights.pop(i)
                        yield HighlightEndEvent()
                        break

        # Emit any remaining source
        if current_pos < len(source):
            yield SourceEvent(start=current_pos, end=len(source))


# Keep the simple Highlighter for backwards compatibility
Highlighter = HighlighterV2
