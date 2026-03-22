from abc import ABC, abstractmethod

from domain.aggregates.cart import Cart
from domain.aggregates.order import Order


class IOrderRepository(ABC):
    @abstractmethod
    async def add(self, order: Order) -> Order:
        pass

    @abstractmethod
    async def get_by_id(self, order_id: int) -> Order | None:
        pass

    @abstractmethod
    async def update(self, order: Order) -> None:
        pass


class ICartRepository(ABC):
    @abstractmethod
    async def get(self, order_id: int) -> Cart | None:
        pass

    @abstractmethod
    async def add(self, order: Cart) -> Cart:
        pass

    @abstractmethod
    async def update(self, order: Cart) -> None:
        pass
