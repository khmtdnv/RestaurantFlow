from dataclasses import dataclass

from domain.aggregates.order import Order


# 1. GET /cart/
@dataclass
class CreateOrderInputDTO:
    user_id: int


@dataclass
class CreateOrderResultDTO:
    order: Order
    payment_url: str | None
