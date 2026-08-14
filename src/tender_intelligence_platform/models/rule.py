from dataclasses import dataclass, field
from typing import Any


@dataclass
class Rule:
    """Represents one configurable business rule."""

    name: str
    field: str
    operator: str

    value: Any = None

    values: list[Any] = field(
        default_factory=list
    )

    required: bool = False