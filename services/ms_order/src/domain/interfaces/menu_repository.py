from abc import ABC, abstractmethod

from domain.entities.menu_item import MenuItem


class IMenuItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> MenuItem | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, item_ids: list[int]) -> list[MenuItem]:
        raise NotImplementedError

    @abstractmethod
    async def upsert_batch(self, items: list[dict]) -> None:
        raise NotImplementedError
