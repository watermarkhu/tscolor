"""Highlight layer management for multi-language support."""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Iterator
import tree_sitter

from .configuration import HighlightConfiguration
from .scope import ScopeStack, LocalScope


@dataclass
class CaptureData:
    """Data about a capture from a query match.

    Attributes:
        node: The tree-sitter node
        capture_name: Name of the capture (e.g., "keyword", "function")
        pattern_index: Index of the pattern that matched
    """

    node: tree_sitter.Node
    capture_name: str
    pattern_index: int


@dataclass(order=True)
class SortableEvent:
    """An event that can be sorted by position and priority.

    Attributes:
        sort_key: Tuple used for sorting (position, event_type, depth)
        event_type: Type of event ("start" or "end")
        position: Byte position in source
        highlight_index: Index into highlight_names list
        depth: Layer depth (for prioritization)
        range: Full byte range (start, end) for deduplication
    """

    sort_key: Tuple[int, int, int] = field(compare=True)
    event_type: str = field(compare=False)
    position: int = field(compare=False)
    highlight_index: int = field(compare=False)
    depth: int = field(compare=False)
    range: Tuple[int, int] = field(compare=False)


class HighlightLayer:
    """A highlighting layer for a single language.

    Each layer represents one language in the document (base language or
    injected language). Layers maintain their own scope stack for local
    variable tracking.

    Attributes:
        config: Highlight configuration for this language
        tree: Parsed syntax tree
        depth: Nesting depth of this layer (0 for base language)
        ranges: Byte ranges that this layer applies to
        scope_stack: Stack of local scopes
    """

    def __init__(
        self,
        config: HighlightConfiguration,
        tree: tree_sitter.Tree,
        depth: int = 0,
        ranges: Optional[List[Tuple[int, int]]] = None,
    ):
        """Initialize a highlight layer.

        Args:
            config: Highlight configuration for this language
            tree: Parsed syntax tree
            depth: Nesting depth (0 for base language)
            ranges: Optional list of byte ranges this layer applies to
        """
        self.config = config
        self.tree = tree
        self.depth = depth
        self.ranges = ranges or [(0, tree.root_node.end_byte)]
        self.scope_stack = ScopeStack()
        self._highlight_end_stack: List[int] = []

    def extract_highlights(self) -> Iterator[CaptureData]:
        """Extract highlight captures from this layer.

        Executes the combined query on the syntax tree and yields capture data.

        Yields:
            CaptureData for each matched capture
        """
        # Execute the highlights query
        captures = self.config.highlights_query.captures(self.tree.root_node)

        for node, capture_name in captures:
            # Check if this node falls within our valid ranges
            if not self._node_in_ranges(node):
                continue

            # Get the pattern index (not directly available in py-tree-sitter)
            # For now, we'll use a default of 0
            pattern_index = 0

            yield CaptureData(
                node=node, capture_name=capture_name, pattern_index=pattern_index
            )

    def _node_in_ranges(self, node: tree_sitter.Node) -> bool:
        """Check if a node falls within valid byte ranges for this layer.

        Args:
            node: The node to check

        Returns:
            True if node is within valid ranges
        """
        node_start = node.start_byte
        node_end = node.end_byte

        for range_start, range_end in self.ranges:
            # Check if node overlaps with this range
            if node_start < range_end and node_end > range_start:
                return True

        return False

    def process_local_scope(self, node: tree_sitter.Node, capture_name: str) -> None:
        """Process a local scope capture.

        Args:
            node: The scope node
            capture_name: Name of the capture
        """
        # Create a new scope
        # Check if it inherits from parent (can be determined by properties)
        inherits = True  # Default to inheriting
        scope = LocalScope(
            inherits=inherits, range=(node.start_byte, node.end_byte)
        )
        self.scope_stack.push(scope)

    def process_local_definition(
        self, node: tree_sitter.Node, capture_name: str
    ) -> None:
        """Process a local variable definition.

        Args:
            node: The definition node
            capture_name: Name of the capture
        """
        if len(self.scope_stack) == 0:
            return

        # Extract variable name (usually from the node's text)
        name = node.text.decode("utf-8", errors="replace")

        # Add definition to current scope
        if self.scope_stack.scopes:
            current_scope = self.scope_stack.scopes[-1]
            current_scope.add_definition(
                name=name, value_range=(node.start_byte, node.end_byte)
            )

    def resolve_local_reference(
        self, node: tree_sitter.Node, capture_name: str
    ) -> Optional[int]:
        """Resolve a local variable reference to a highlight index.

        Args:
            node: The reference node
            capture_name: Name of the capture

        Returns:
            Highlight index if found, None otherwise
        """
        # Extract variable name
        name = node.text.decode("utf-8", errors="replace")

        # Search scope stack for definition
        definition = self.scope_stack.find_definition(name, node.start_byte)

        if definition and definition.highlight_index is not None:
            return definition.highlight_index

        return None

    def sort_key(self, position: int, is_end: bool) -> Tuple[int, int, int]:
        """Generate a sort key for an event.

        Args:
            position: Byte position
            is_end: True if this is an end event

        Returns:
            Sort key tuple (position, event_type_priority, depth)
        """
        # End events come before start events at the same position
        event_priority = 0 if is_end else 1
        return (position, event_priority, self.depth)
