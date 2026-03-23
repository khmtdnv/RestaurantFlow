from dataclasses import dataclass, field
from decimal import Decimal

from domain.entities.cart_item import CartItem


@dataclass
class Cart:
    """Cart aggregate linked to user."""

    # user_id needs to be extracted from request header "X-User-Id"
    user_id: int
    items: list[CartItem] = field(default_factory=list)
    # init=False means we can't specify total price when creating cart
    # we can't do Cart(user_id=1, total_price=Decimal("9999")) or we will get TypeError
    total_price: Decimal = field(init=False)

    def __post_init__(self) -> None:
        """This is going to be called right after (__init__)."""
        # this is consequence of making total_price init=False
        self._calculate_total()

    def _calculate_total(self) -> None:
        """total_price value calculator."""
        total = sum(item.price * item.quantity for item in self.items)
        self.total_price = Decimal(total)

    def add_item(self, dish_id: int, quantity: int, price: Decimal) -> None:
        """Business logic of adding CartItem entity to Cart aggregate."""
        if quantity <= 0:
            raise ValueError("Dish quantity must be postive int.")

        existing_item = next((item for item in self.items if item.dish_id == dish_id), None)

        if existing_item:
            existing_item.quantity += quantity
            existing_item.price = price
        else:
            new_item = CartItem(dish_id=dish_id, quantity=quantity, price=price)
            self.items.append(new_item)

        self._calculate_total()
