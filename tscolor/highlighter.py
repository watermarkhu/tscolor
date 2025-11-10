"""Enhanced syntax highlighting engine with multi-layer support."""

from collections.abc import Callable, Iterator
import tree_sitter

from .configuration import HighlightConfiguration
from .events import HighlightEvent, SourceEvent, HighlightStartEvent, HighlightEndEvent
from .layer import HighlightLayer, SortableEvent, CaptureData


class Highlighter:
    """Enhanced syntax highlighter with multi-layer support.

    This highlighter supports:
    - Language injection (embedding one language in another)
    - Local variable scope tracking
    - Multi-layer processing with proper prioritization
    - Overlapping highlight deduplication

    Example:
        >>> highlighter = Highlighter()
        >>> config = HighlightConfiguration(...)
        >>> source = b"def hello(): pass"
        >>> for event in highlighter.highlight(config, source):
        ...     # Process highlight events
        ...     pass
    """

    def __init__(self) -> None:
        """Initialize a new highlighter instance."""
        self.parser = tree_sitter.Parser()
        self._injection_configs: dict[str, HighlightConfiguration] = {}

    def _resolve_highlight_index(
        self, capture_name: str, capture_index_map: dict[str, int]
    ) -> int | None:
        """Resolve a capture name to a highlight index with hierarchical fallback.

        Implements hierarchical matching like tree-sitter-highlight:
        - First tries exact match (e.g., "function.call")
        - Falls back to parent (e.g., "function" for "function.call")
        - Continues up the hierarchy until a match is found or exhausted

        Args:
            capture_name: The capture name from the query (e.g., "function.call")
            capture_index_map: Mapping from capture names to highlight indices

        Returns:
            Highlight index if found, None otherwise
        """
        # Try exact match first
        if capture_name in capture_index_map:
            return capture_index_map[capture_name]

        # Try hierarchical fallback
        # For "function.call.method", try "function.call", then "function"
        parts = capture_name.split(".")
        for i in range(len(parts) - 1, 0, -1):
            parent_name = ".".join(parts[:i])
            if parent_name in capture_index_map:
                return capture_index_map[parent_name]

        return None

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
        cancellation_flag: Callable[[], bool] | None = None,
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
    ) -> list[HighlightLayer]:
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
        language_ranges: dict[str, list[tuple[int, int]]] = {}

        # Convert matches to (node, capture_name) tuples and process
        for pattern_index, captures_dict in matches:
            for capture_name, nodes in captures_dict.items():
                for node in nodes:
                    # Look for injection.language captures
                    if capture_name == "injection.language":
                        if node.text:
                            lang_name = node.text.decode("utf-8", errors="replace")
                        else:
                            continue
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
        self, layers: list[HighlightLayer], source: bytes
    ) -> list[SortableEvent]:
        """Collect and sort events from all layers.

        Args:
            layers: List of highlight layers
            source: Source code bytes

        Returns:
            Sorted list of events
        """
        events = []

        for layer in layers:
            # First, collect all captures and deduplicate by node position
            # When multiple captures match the same node, keep the one with highest pattern_index
            node_captures: dict[tuple[int, int], tuple[CaptureData, int]] = {}

            for capture_data in layer.extract_highlights():
                node = capture_data.node
                capture_name = capture_data.capture_name
                node_key = (node.start_byte, node.end_byte)

                # Handle local scope captures immediately (don't deduplicate)
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
                    node_captures[node_key] = (capture_data, highlight_index)
                else:
                    # Regular highlight capture with hierarchical matching
                    highlight_index = self._resolve_highlight_index(
                        capture_name, layer.config.capture_index_map
                    )
                    if highlight_index is None:
                        continue

                    # Keep this capture if it's the first or has higher pattern_index
                    if node_key not in node_captures:
                        node_captures[node_key] = (capture_data, highlight_index)
                    else:
                        existing_capture, existing_index = node_captures[node_key]
                        # Higher pattern_index = later in query = higher priority
                        if capture_data.pattern_index >= existing_capture.pattern_index:
                            node_captures[node_key] = (capture_data, highlight_index)

            # Now create events from deduplicated captures
            for (start_byte, end_byte), (
                capture_data,
                highlight_index,
            ) in node_captures.items():
                start_event = SortableEvent(
                    sort_key=layer.sort_key(start_byte, is_end=False),
                    event_type="start",
                    position=start_byte,
                    highlight_index=highlight_index,
                    depth=layer.depth,
                    range=(start_byte, end_byte),
                )

                end_event = SortableEvent(
                    sort_key=layer.sort_key(end_byte, is_end=True),
                    event_type="end",
                    position=end_byte,
                    highlight_index=highlight_index,
                    depth=layer.depth,
                    range=(start_byte, end_byte),
                )

                events.append(start_event)
                events.append(end_event)

        # Sort all events
        events.sort()

        return events

    def _emit_events(
        self,
        source: bytes,
        sorted_events: list[SortableEvent],
        cancellation_flag: Callable[[], bool] | None,
        byte_range: tuple[int, int] | None = None,
    ) -> Iterator[HighlightEvent]:
        """Emit highlight events, handling overlaps and deduplication.

        Args:
            source: Source code bytes
            sorted_events: Sorted list of events
            cancellation_flag: Optional cancellation check
            byte_range: Optional (start, end) byte range to constrain events

        Yields:
            HighlightEvent objects
        """
        # Determine the range to process
        start_byte, end_byte = byte_range if byte_range else (0, len(source))

        if not sorted_events:
            # No highlights, emit entire range
            if start_byte < end_byte:
                yield SourceEvent(start=start_byte, end=end_byte)
            return

        current_pos = start_byte
        active_highlights: list[tuple[int, int, int]] = []  # (end, index, depth)
        seen_ranges: set[tuple[int, int, int]] = set()  # (start, end, depth)

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

        # Emit any remaining source within the byte range
        end_byte = byte_range[1] if byte_range else len(source)
        if current_pos < end_byte:
            yield SourceEvent(start=current_pos, end=end_byte)

    def highlight_node(
        self,
        config: HighlightConfiguration,
        node: tree_sitter.Node,
        tree: tree_sitter.Tree,
        cancellation_flag: Callable[[], bool] | None = None,
    ) -> Iterator[HighlightEvent]:
        """Highlight a specific tree-sitter node.

        This method allows highlighting of an individual node from an already-parsed
        tree, rather than parsing an entire source file. This is useful when you want
        to highlight a specific AST node or a subsection of code.

        Args:
            config: Highlight configuration for the language
            node: Tree-sitter node to highlight
            tree: Tree-sitter tree containing the node
            cancellation_flag: Optional callable that returns True to cancel

        Yields:
            HighlightEvent objects describing how to highlight the node

        Example:
            >>> # Parse code first
            >>> parser = tree_sitter.Parser(tree_sitter.Language(ts_python.language()))
            >>> tree = parser.parse(b"def hello(): pass")
            >>> func_node = tree.root_node.children[0]  # Get function node
            >>>
            >>> # Highlight just that node
            >>> highlighter = Highlighter()
            >>> config = get_configuration("python")
            >>> events = highlighter.highlight_node(config, func_node, tree")
        """
        # Create a layer for this specific node
        # We need to parse the source to get the tree, then use the node's
        # byte range to constrain highlights to just that node

        # Set the parser language and parse the source
        self.parser.language = config.language

        start_byte = node.start_byte
        end_byte = node.end_byte

        # Create a layer with restricted range
        layer = HighlightLayer(
            config=config,
            tree=tree,
            depth=0,
            ranges=[(start_byte, end_byte)],
        )

        layers = [layer]

        # Extract and sort all highlight events from all layers
        events = self._collect_events_from_layers(layers, tree.root_node.text)

        # Deduplicate and emit events within the node's byte range
        yield from self._emit_events(
            tree.root_node.text, events, cancellation_flag, byte_range=(start_byte, end_byte)
        )
