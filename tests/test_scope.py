"""Tests for local scope tracking."""

from tscolor.scope import LocalScope, LocalDefinition, ScopeStack


class TestLocalDefinition:
    """Test LocalDefinition class."""

    def test_create_definition(self):
        """Test creating a local definition."""
        defn = LocalDefinition(name="foo", value_range=(10, 15))
        assert defn.name == "foo"
        assert defn.value_range == (10, 15)
        assert defn.highlight_index is None

    def test_definition_with_highlight(self):
        """Test creating a definition with highlight."""
        defn = LocalDefinition(name="bar", value_range=(20, 25), highlight_index=3)
        assert defn.name == "bar"
        assert defn.highlight_index == 3


class TestLocalScope:
    """Test LocalScope class."""

    def test_create_scope(self):
        """Test creating a local scope."""
        scope = LocalScope(inherits=True, range=(0, 100))
        assert scope.inherits is True
        assert scope.range == (0, 100)
        assert len(scope.definitions) == 0

    def test_add_definition(self):
        """Test adding a definition to scope."""
        scope = LocalScope(inherits=False, range=(0, 100))
        defn = scope.add_definition("var", (10, 15))

        assert defn.name == "var"
        assert len(scope.definitions) == 1
        assert scope.definitions[0] == defn

    def test_find_definition_exists(self):
        """Test finding an existing definition."""
        scope = LocalScope(inherits=True, range=(0, 100))
        scope.add_definition("foo", (10, 20))

        # Reference after definition
        found = scope.find_definition("foo", 25)
        assert found is not None
        assert found.name == "foo"

    def test_find_definition_not_exists(self):
        """Test finding a non-existent definition."""
        scope = LocalScope(inherits=True, range=(0, 100))
        scope.add_definition("foo", (10, 20))

        found = scope.find_definition("bar", 25)
        assert found is None

    def test_find_definition_before_value(self):
        """Test that references before value range don't match."""
        scope = LocalScope(inherits=True, range=(0, 100))
        scope.add_definition("foo", (10, 20))

        # Reference before value range ends
        found = scope.find_definition("foo", 15)
        assert found is None


class TestScopeStack:
    """Test ScopeStack class."""

    def test_create_stack(self):
        """Test creating an empty scope stack."""
        stack = ScopeStack()
        assert len(stack) == 0

    def test_push_scope(self):
        """Test pushing scopes onto stack."""
        stack = ScopeStack()
        scope1 = LocalScope(inherits=True, range=(0, 100))
        scope2 = LocalScope(inherits=True, range=(10, 50))

        stack.push(scope1)
        assert len(stack) == 1

        stack.push(scope2)
        assert len(stack) == 2

    def test_pop_scope(self):
        """Test popping scopes from stack."""
        stack = ScopeStack()
        scope1 = LocalScope(inherits=True, range=(0, 100))
        scope2 = LocalScope(inherits=True, range=(10, 50))

        stack.push(scope1)
        stack.push(scope2)

        popped = stack.pop()
        assert popped == scope2
        assert len(stack) == 1

    def test_pop_empty_stack(self):
        """Test popping from empty stack."""
        stack = ScopeStack()
        popped = stack.pop()
        assert popped is None

    def test_find_definition_in_current_scope(self):
        """Test finding definition in current scope."""
        stack = ScopeStack()
        scope = LocalScope(inherits=True, range=(0, 100))
        scope.add_definition("foo", (10, 20))
        stack.push(scope)

        found = stack.find_definition("foo", 25)
        assert found is not None
        assert found.name == "foo"

    def test_find_definition_in_parent_scope(self):
        """Test finding definition in parent scope (inheritance)."""
        stack = ScopeStack()

        # Parent scope with definition
        parent = LocalScope(inherits=True, range=(0, 100))
        parent.add_definition("foo", (10, 20))
        stack.push(parent)

        # Child scope inherits from parent
        child = LocalScope(inherits=True, range=(30, 80))
        stack.push(child)

        # Should find definition from parent scope
        found = stack.find_definition("foo", 50)
        assert found is not None
        assert found.name == "foo"

    def test_find_definition_no_inheritance(self):
        """Test that non-inheriting scopes block parent lookup."""
        stack = ScopeStack()

        # Parent scope with definition
        parent = LocalScope(inherits=True, range=(0, 100))
        parent.add_definition("foo", (10, 20))
        stack.push(parent)

        # Child scope does NOT inherit
        child = LocalScope(inherits=False, range=(30, 80))
        stack.push(child)

        # Should NOT find definition from parent scope
        found = stack.find_definition("foo", 50)
        assert found is None

    def test_clear_stack(self):
        """Test clearing the scope stack."""
        stack = ScopeStack()
        stack.push(LocalScope(inherits=True, range=(0, 100)))
        stack.push(LocalScope(inherits=True, range=(10, 50)))

        assert len(stack) == 2
        stack.clear()
        assert len(stack) == 0

    def test_shadowing(self):
        """Test that inner definitions shadow outer ones."""
        stack = ScopeStack()

        # Outer scope
        outer = LocalScope(inherits=True, range=(0, 100))
        outer_def = outer.add_definition("x", (5, 10))
        outer_def.highlight_index = 1
        stack.push(outer)

        # Inner scope with same variable name
        inner = LocalScope(inherits=True, range=(20, 80))
        inner_def = inner.add_definition("x", (25, 30))
        inner_def.highlight_index = 2
        stack.push(inner)

        # Should find inner definition
        found = stack.find_definition("x", 50)
        assert found is not None
        assert found.highlight_index == 2
