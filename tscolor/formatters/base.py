"""Base formatter protocol and classes."""

from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from ..configuration import HighlightConfiguration
from ..events import HighlightEvent
from ..theme import Theme


@runtime_checkable
class Formatter(Protocol):
    """Protocol for syntax highlight formatters.

    All formatters must implement this protocol to be compatible with TSColor.
    """

    theme: Theme

    def format(
        self,
        source: bytes,
        events: Iterator[HighlightEvent],
        config: HighlightConfiguration,
    ) -> str:
        """Format highlighted code.

        Args:
            source: Source code bytes
            events: Iterator of highlight events
            config: Language configuration

        Returns:
            Formatted output string
        """
        ...
