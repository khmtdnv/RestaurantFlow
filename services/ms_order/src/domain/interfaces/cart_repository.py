from abc import ABC, abstractmethod

from domain.aggregates.cart import Cart


class ICartRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Cart | None:
        """Searches for existing cart for user. If there is no cart returns None."""
        raise NotImplementedError

    async def get_or_create_by_user_id(self, user_id: int) -> Cart:
        """Searches for existing cart for user. If there is no cart, it creates new one and returns it."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, cart: Cart) -> None:
        """Saves the entire aggregate state."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        """Deletes cart for user (for example, cart can be deleted after created order)"""
        raise NotImplementedError
