from abc import ABC, abstractmethod
from decimal import Decimal


class IPaymentClient(ABC):
    @abstractmethod
    async def create_payment(self, order_id: int, amount: Decimal) -> str | None:
        raise NotImplementedError
