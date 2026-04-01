from abc import ABC, abstractmethod

from domain.entities import Transaction


class IPaymentGateway(ABC):
    @abstractmethod
    async def generate_payment_link(self, order_id: str, amount: str) -> Transaction | None:
        """Возвращает транзакцию с заполненным payment_url"""
        pass
