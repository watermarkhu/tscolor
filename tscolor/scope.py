"""Local scope tracking for variable highlighting."""
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class LocalDefinition:
    """A local variable definition.

    Attributes:
        name: Variable name
        value_range: Byte range of the value (for references to check against)
        highlight_index: Optional highlight index for this variable
    """

    name: str
    value_range: Tuple[int, int]
    highlight_index: Optional[int] = None


@dataclass
class LocalScope:
    """A local scope tracking variable definitions.

    Attributes:
        inherits: Whether this scope inherits from parent scope
        range: Byte range of this scope
        definitions: List of variable definitions in this scope
    """

    inherits: bool
    range: Tuple[int, int]
    definitions: List[LocalDefinition]

    def __init__(self, inherits: bool, range: Tuple[int, int]):
        """Initialize a local scope.

        Args:
            inherits: Whether to inherit parent scope definitions
            range: Byte range (start, end) of this scope
        """
        self.inherits = inherits
        self.range = range
        self.definitions = []

    def add_definition(self, name: str, value_range: Tuple[int, int]) -> LocalDefinition:
        """Add a variable definition to this scope.

        Args:
            name: Variable name
            value_range: Byte range of the variable's value

        Returns:
            The created LocalDefinition
        """
        definition = LocalDefinition(name=name, value_range=value_range)
        self.definitions.append(definition)
        return definition

    def find_definition(self, name: str, position: int) -> Optional[LocalDefinition]:
        """Find a variable definition in this scope.

        Args:
            name: Variable name to find
            position: Byte position of the reference

        Returns:
            LocalDefinition if found and position is valid, None otherwise
        """
        for definition in self.definitions:
            # Reference must come after the definition's value range
            if definition.name == name and position >= definition.value_range[1]:
                return definition
        return None


class ScopeStack:
    """Stack of local scopes for tracking variable definitions.

    This class manages a stack of scopes, allowing for nested scope creation
    and variable resolution.
    """

    def __init__(self):
        """Initialize an empty scope stack."""
        self.scopes: List[LocalScope] = []

    def push(self, scope: LocalScope) -> None:
        """Push a new scope onto the stack.

        Args:
            scope: The scope to push
        """
        self.scopes.append(scope)

    def pop(self) -> Optional[LocalScope]:
        """Pop the top scope from the stack.

        Returns:
            The popped scope, or None if stack is empty
        """
        if self.scopes:
            return self.scopes.pop()
        return None

    def find_definition(self, name: str, position: int) -> Optional[LocalDefinition]:
        """Find a variable definition by searching the scope stack.

        Searches from the top of the stack (innermost scope) to the bottom,
        respecting scope inheritance rules.

        Args:
            name: Variable name to find
            position: Byte position of the reference

        Returns:
            LocalDefinition if found, None otherwise
        """
        # Search from innermost to outermost scope
        for i in range(len(self.scopes) - 1, -1, -1):
            scope = self.scopes[i]
            definition = scope.find_definition(name, position)
            if definition:
                return definition

            # Stop searching if this scope doesn't inherit
            if not scope.inherits:
                break

        return None

    def clear(self) -> None:
        """Clear all scopes from the stack."""
        self.scopes.clear()

    def __len__(self) -> int:
        """Get the number of scopes in the stack."""
        return len(self.scopes)
