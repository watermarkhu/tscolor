"""Highlight events generated during syntax highlighting."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Union


class EventType(Enum):
    """Type of highlight event."""

    SOURCE = auto()
    HIGHLIGHT_START = auto()
    HIGHLIGHT_END = auto()


@dataclass
class SourceEvent:
    """Event representing a range of source code.

    Attributes:
        start: Start byte offset in the source code
        end: End byte offset in the source code
    """

    start: int
    end: int


@dataclass
class HighlightStartEvent:
    """Event representing the start of a highlight region.

    Attributes:
        index: Index into the highlight names list
    """

    index: int


@dataclass
class HighlightEndEvent:
    """Event representing the end of a highlight region."""

    pass


# Type alias for any highlight event
HighlightEvent = Union[SourceEvent, HighlightStartEvent, HighlightEndEvent]
