from dataclasses import dataclass


# 1. GET /cart/
@dataclass
class CreateOrderInputDTO:
    user_id: int
