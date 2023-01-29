"""Pytekukko exceptions."""

from typing import Any


class UnexpectedResponseStructureError(ValueError):
    """Error for signaling unexpected response structure."""

    def __init__(self, data: Any) -> None:
        """Construct new unexpected response structure error."""
        super().__init__(f"Unexpected response structure, got {type(data)}")
