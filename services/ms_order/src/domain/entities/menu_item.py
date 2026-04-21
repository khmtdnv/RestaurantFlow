from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MenuItem:
    """Read only model for menu snapshot."""

    id: int
    price: Decimal
    is_available: bool
