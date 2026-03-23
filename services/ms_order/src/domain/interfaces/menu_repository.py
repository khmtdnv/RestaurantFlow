from abc import ABC, abstractmethod

from domain.entities.menu_item import MenuItem


class IMenuItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> MenuItem | None:
        pass
