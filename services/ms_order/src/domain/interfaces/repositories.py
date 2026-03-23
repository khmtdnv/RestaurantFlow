from abc import ABC, abstractmethod

from domain.aggregates.cart import Cart
from domain.aggregates.order import Order
from domain.entities.menu_item import MenuItem

# !Агрегат инкапсулирует поведение и состояние бизнеса.
# !Репозиторий инкапсулирует хранение этого состояния.


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
    async def get_by_user_id(self, user_id: int) -> Cart:
        """Searches for existing cart for user. If there is no cart, it creates new one and returns it."""
        pass

    @abstractmethod
    async def save(self, cart: Cart) -> None:
        """Saves the entire aggregate state."""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        """Deletes cart for user (for example, cart can be deleted after created order)"""
        pass


class IMenuItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> MenuItem | None:
        pass
