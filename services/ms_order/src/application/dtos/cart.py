from dataclasses import dataclass


# 1. GET /cart/
@dataclass
class GetCartInputDTO:
    user_id: int


# 2. POST /cart/items/
@dataclass
class AddItemToCartInputDTO:
    user_id: int
    dish_id: int
    quantity: int
