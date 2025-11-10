"""Tests for HighlightLayer."""

import pytest
import tree_sitter

from tscolor.layer import HighlightLayer
from tscolor.configuration import HighlightConfiguration


class TestHighlightLayerWithRanges:
    """Test HighlightLayer with custom byte ranges."""

    @pytest.fixture
    def python_config(self, tree_sitter_python):
        """Create a Python configuration."""
        lang = tree_sitter.Language(tree_sitter_python.language())
        highlights_query = "(identifier) @variable"
        return HighlightConfiguration(language=lang, highlights_query=highlights_query)

    @pytest.fixture
    def python_tree(self, tree_sitter_python):
        """Parse Python code."""
        lang = tree_sitter.Language(tree_sitter_python.language())
        parser = tree_sitter.Parser(lang)
        return parser.parse(b"def hello():\n    x = 1\n    y = 2")

    def test_layer_with_restricted_ranges(self, python_config, python_tree):
        """Test layer that only highlights within specific byte ranges."""
        # Create a layer that only processes bytes 0-15 (first line)
        layer = HighlightLayer(config=python_config, tree=python_tree, ranges=[(0, 15)])

        # Extract highlights
        captures = list(layer.extract_highlights())

        # Should only have captures from the first line
        for capture in captures:
            assert capture.node.start_byte < 15

    def test_node_not_in_ranges(self, python_config, python_tree):
        """Test that nodes outside ranges are filtered out."""
        # Create a layer with a range that excludes most of the code
        layer = HighlightLayer(config=python_config, tree=python_tree, ranges=[(0, 1)])

        # Should have very few or no captures
        captures = list(layer.extract_highlights())
        assert len(captures) <= 1  # Maybe just 'def' or nothing


class TestLocalScopeTracking:
    """Test local scope processing."""

    @pytest.fixture
    def python_lang(self, tree_sitter_python):
        """Get Python language."""
        return tree_sitter.Language(tree_sitter_python.language())

    @pytest.fixture
    def python_tree(self, python_lang):
        """Parse Python code with function."""
        parser = tree_sitter.Parser(python_lang)
        return parser.parse(b"def foo(x):\n    y = x + 1\n    return y")

    def test_process_local_scope(self, python_lang, python_tree):
        """Test processing a local scope capture."""
        config = HighlightConfiguration(
            language=python_lang, highlights_query="(identifier) @variable"
        )
        layer = HighlightLayer(config=config, tree=python_tree)

        # Get the function node
        func_node = python_tree.root_node.children[0]

        # Process it as a local scope
        layer.process_local_scope(func_node, "local.scope")

        # Should have added a scope
        assert len(layer.scope_stack.scopes) == 1
        assert layer.scope_stack.scopes[0].range == (
            func_node.start_byte,
            func_node.end_byte,
        )

    def test_process_local_definition_with_scope(self, python_lang, python_tree):
        """Test processing a local variable definition within a scope."""
        config = HighlightConfiguration(
            language=python_lang, highlights_query="(identifier) @variable"
        )
        layer = HighlightLayer(config=config, tree=python_tree)

        # First create a scope
        func_node = python_tree.root_node.children[0]
        layer.process_local_scope(func_node, "local.scope")

        # Find any identifier node with text
        # Just iterate through all nodes to find one we can use
        def find_identifier(node):
            if node.type == "identifier" and node.text:
                return node
            for child in node.children:
                result = find_identifier(child)
                if result:
                    return result
            return None

        identifier = find_identifier(func_node)
        assert identifier is not None, "Should find an identifier"

        # Process it as a local definition
        layer.process_local_definition(identifier, "local.definition")

        # Should have added a definition to the scope
        scope = layer.scope_stack.scopes[0]
        assert len(scope.definitions) >= 1

    def test_process_local_definition_without_scope(self, python_lang, python_tree):
        """Test processing a local definition when no scope exists."""
        config = HighlightConfiguration(
            language=python_lang, highlights_query="(identifier) @variable"
        )
        layer = HighlightLayer(config=config, tree=python_tree)

        # Don't create a scope first

        # Find an identifier node
        assignment = (
            python_tree.root_node.children[0].child_by_field_name("body").children[1]
        )
        identifier = assignment.child_by_field_name("left")

        # Process it as a local definition - should return early
        layer.process_local_definition(identifier, "local.definition")

        # Scope stack should still be empty
        assert len(layer.scope_stack.scopes) == 0

    def test_process_local_definition_empty_scope_stack(self, python_lang):
        """Test processing a local definition when scope stack is empty (early return)."""
        parser = tree_sitter.Parser(python_lang)
        tree = parser.parse(b"x = 1")

        config = HighlightConfiguration(
            language=python_lang, highlights_query="(identifier) @variable"
        )
        layer = HighlightLayer(config=config, tree=tree)

        # Don't create any scope - scope stack is empty
        # Find any identifier
        def find_identifier(node):
            if node.type == "identifier":
                return node
            for child in node.children:
                result = find_identifier(child)
                if result:
                    return result
            return None

        identifier = find_identifier(tree.root_node)
        # Process it - should return early because scope stack is empty
        layer.process_local_definition(identifier, "local.definition")

        # Scope stack should still be empty
        assert len(layer.scope_stack.scopes) == 0

    def test_resolve_local_reference_found(self, python_lang):
        """Test resolving a local reference that exists in scope."""
        parser = tree_sitter.Parser(python_lang)
        tree = parser.parse(b"x = 1\ny = x")

        config = HighlightConfiguration(
            language=python_lang, highlights_query="(identifier) @variable"
        )
        layer = HighlightLayer(config=config, tree=tree)

        # Create a scope
        layer.process_local_scope(tree.root_node, "local.scope")

        # Find 'x' identifier in first assignment and add as definition
        def find_all_identifiers(node):
            result = []
            if node.type == "identifier":
                result.append(node)
            for child in node.children:
                result.extend(find_all_identifiers(child))
            return result

        identifiers = find_all_identifiers(tree.root_node)
        x_def = identifiers[0]  # First 'x' in "x = 1"
        x_ref = identifiers[2]  # Second 'x' in "y = x"

        # Add definition
        layer.process_local_definition(x_def, "local.definition")

        # Set a highlight index
        scope = layer.scope_stack.scopes[0]
        scope.definitions[0].highlight_index = 5

        # Resolve reference
        result = layer.resolve_local_reference(x_ref, "local.reference")
        assert result == 5

    def test_resolve_local_reference_not_found(self, python_lang):
        """Test resolving a local reference that doesn't exist."""
        parser = tree_sitter.Parser(python_lang)
        tree = parser.parse(b"y = x")

        config = HighlightConfiguration(
            language=python_lang, highlights_query="(identifier) @variable"
        )
        layer = HighlightLayer(config=config, tree=tree)

        # Create a scope but don't add any definitions
        layer.process_local_scope(tree.root_node, "local.scope")

        # Find 'x' reference
        def find_identifier(node):
            if node.type == "identifier" and node.text == b"x":
                return node
            for child in node.children:
                result = find_identifier(child)
                if result:
                    return result
            return None

        x_ref = find_identifier(tree.root_node)
        assert x_ref is not None

        # Should return None since no definition exists
        result = layer.resolve_local_reference(x_ref, "local.reference")
        assert result is None
