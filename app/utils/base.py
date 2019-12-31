"""General utilities."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Return:
    """Used to return standard parameters from functions."""

    success: bool
    message: str
    data: Any
