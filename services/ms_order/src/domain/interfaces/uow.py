from abc import ABC, abstractmethod

from domain.interfaces.repositories import ICartRepository, IOrderRepository


class IUnitOfWork(ABC):
    order: IOrderRepository
    cart: ICartRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass
