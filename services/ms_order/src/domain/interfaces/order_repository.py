from abc import ABC, abstractmethod

from domain.aggregates.order import Order


class IOrderRepository(ABC):
    @abstractmethod
    async def create(self, order: Order) -> int:
        raise NotImplementedError

    # @abstractmethod
    # async def get_by_id(self, order_id: int) -> Order | None:
    #     raise NotImplementedError

    # @abstractmethod
    # async def update(self, order: Order) -> None:
    #     raise NotImplementedError
