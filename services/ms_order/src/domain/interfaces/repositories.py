from abc import ABC, abstractmethod

from domain.aggregates.order import Order


class IOrderRepository(ABC):
    @abstractmethod
    async def add(self, order: Order) -> Order:
        pass
